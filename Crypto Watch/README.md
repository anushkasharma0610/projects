# CryptoWatch

CryptoWatch is a simple local dashboard for building a personal cryptocurrency watchlist, reviewing market information, seeing transparent next-day statistical estimates, and trying hypothetical SIP or lumpsum growth calculations. It is an analytics application only: it does not trade, custody, or give financial advice.

## Stack

- Frontend: React, Vite, React Router, Recharts, CSS
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT, bcrypt hashing, HTTPX
- Database: SQLite (`backend/crypto_watchlist.db`, created automatically)
- Market data: Alpha Vantage Digital Currency API

## Project structure

```
backend/     FastAPI API, services, SQLite database
frontend/    Vite React application
```

## Setup

Copy `backend/.env.example` to `backend/.env`, set a strong `SECRET_KEY`, and add your required `ALPHA_VANTAGE_API_KEY`. Copy `frontend/.env.example` to `frontend/.env` if the API is not at `http://localhost:8000`.

Start the backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

On macOS/Linux activate with `source venv/bin/activate`. Starting FastAPI automatically creates `crypto_watchlist.db`; no database server, Docker, PostgreSQL, or pgAdmin is needed.

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## How it works

Passwords are bcrypt hashes, never plaintext. Login returns a short-lived JWT saved in browser local storage; protected API calls send it as a bearer token. Each watchlist query is filtered by the authenticated user, and a database constraint prevents duplicate coins per user.

Market data is requested through `crypto_service.py`, which uses Alpha Vantage's `DIGITAL_CURRENCY_DAILY` endpoint and an in-memory cache. Alpha Vantage identifies assets by symbol (such as `BTC`) and does not supply logos, market caps, or a global crypto screener in this endpoint, so unavailable fields are shown as unavailable rather than fabricated. Missing/rate-limited market data displays a friendly API error.

The next-day estimate is deliberately deterministic, not trained machine learning. `prediction_service.py` compares 7- and 14-day moving averages, short momentum, recent change, and volatility. Volatility lowers the proposed movement/confidence; outputs are capped and labeled as estimates, not guarantees.

Lumpsum uses `FV = P × (1 + r)^n`. SIP adds each monthly investment and compounds it at the monthly equivalent rate. Both calculations run on the backend and return annual chart points. Calculator currency labels support INR and USD; no exchange rate conversion is implied.

## API endpoints

| Area | Endpoint |
|---|---|
| Authentication | `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me` |
| Watchlist | `GET /api/watchlist`, `POST /api/watchlist`, `DELETE /api/watchlist/{coin_id}` |
| Crypto | `GET /api/crypto/search`, `/api/crypto/markets`, `/api/crypto/{coin_id}`, `/history`, `/prediction` |
| Calculator | `POST /api/calculator/lumpsum`, `POST /api/calculator/sip` |

Crypto and investment values are informational, hypothetical, and can differ materially from real outcomes.
