import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from auth import create_access_token, get_current_user, hash_password, verify_password
from calculator_service import calculate_lumpsum, calculate_sip
from crypto_service import get_coin, get_history, get_markets, search_coins
from database import Base, engine, get_db
from models import User, Watchlist
from prediction_service import calculate_prediction
from schemas import LoginRequest, LumpsumRequest, SipRequest, SignupRequest, UserResponse, WatchlistCreate

load_dotenv()

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="CryptoWatch API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(409, "An account with this email already exists.")
    user = User(name=payload.name, email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user); db.commit()
    return {"message": "Account created successfully. Please sign in."}


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password.")
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "user": UserResponse.model_validate(user).model_dump()}


@app.get("/api/auth/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user


@app.get("/api/watchlist")
async def list_watchlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Watchlist).filter(Watchlist.user_id == user.id).order_by(Watchlist.added_at.desc()).all()
    result = []
    for row in rows:
        try:
            coin = await get_coin(row.coin_id)
            # Estimates are calculated on demand, never persisted as market truth.
            try:
                estimate = calculate_prediction(row.coin_id, coin["current_price"], (await get_history(row.coin_id, 30)).get("prices", []))
                coin.update(estimate)
            except (HTTPException, ValueError):
                pass
            result.append({**coin, "added_at": row.added_at})
        except HTTPException as exc:
            result.append({"id": row.coin_id, "name": row.name, "symbol": row.symbol, "market_error": exc.detail})
    return result


@app.post("/api/watchlist", status_code=status.HTTP_201_CREATED)
def add_watchlist(payload: WatchlistCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exists = db.query(Watchlist).filter(Watchlist.user_id == user.id, Watchlist.coin_id == payload.coin_id).first()
    if exists:
        raise HTTPException(409, "This cryptocurrency is already in your watchlist.")
    row = Watchlist(user_id=user.id, coin_id=payload.coin_id, name=payload.name, symbol=payload.symbol.upper())
    db.add(row); db.commit()
    return {"message": "Added to your watchlist."}


@app.delete("/api/watchlist/{coin_id}")
def remove_watchlist(coin_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(Watchlist).filter(Watchlist.user_id == user.id, Watchlist.coin_id == coin_id).first()
    if not row:
        raise HTTPException(404, "This cryptocurrency is not in your watchlist.")
    db.delete(row); db.commit()
    return {"message": "Removed from your watchlist."}


@app.get("/api/crypto/search")
async def crypto_search(q: str = Query(min_length=1, max_length=100)):
    return await search_coins(q)


@app.get("/api/crypto/markets")
async def markets():
    return await get_markets()


@app.get("/api/crypto/{coin_id}")
async def crypto_details(coin_id: str):
    return await get_coin(coin_id)


@app.get("/api/crypto/{coin_id}/history")
async def crypto_history(coin_id: str, days: int = Query(30, ge=1, le=365)):
    return await get_history(coin_id, days)


@app.get("/api/crypto/{coin_id}/prediction")
async def crypto_prediction(coin_id: str):
    coin = await get_coin(coin_id)
    history = await get_history(coin_id, 30)
    try:
        return calculate_prediction(coin_id, coin["current_price"], history.get("prices", []))
    except ValueError as exc:
        raise HTTPException(422, str(exc))


@app.post("/api/calculator/lumpsum")
def lumpsum(payload: LumpsumRequest):
    return calculate_lumpsum(payload.investment, payload.annual_return, payload.years)


@app.post("/api/calculator/sip")
def sip(payload: SipRequest):
    return calculate_sip(payload.monthly_investment, payload.annual_return, payload.years)
