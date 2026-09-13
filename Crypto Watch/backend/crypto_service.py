"""Alpha Vantage crypto client with a small in-memory TTL cache."""
import os
import time
from datetime import datetime, timezone
import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()
BASE_URL = "https://www.alphavantage.co/query"
_cache = {}

# These names support search only; no prices or market figures are hardcoded.
KNOWN_COINS = {"BTC":"Bitcoin", "ETH":"Ethereum", "SOL":"Solana", "XRP":"XRP", "ADA":"Cardano", "DOGE":"Dogecoin", "AVAX":"Avalanche", "DOT":"Polkadot", "LINK":"Chainlink", "LTC":"Litecoin", "BCH":"Bitcoin Cash", "XLM":"Stellar", "MATIC":"Polygon", "ATOM":"Cosmos", "UNI":"Uniswap"}
ALIASES = {name.lower(): symbol for symbol, name in KNOWN_COINS.items()}


def _symbol(value: str) -> str:
    return ALIASES.get(value.strip().lower(), value.strip().upper())


async def _query(params: dict, ttl=300):
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise HTTPException(503, "Market data is not configured. Add ALPHA_VANTAGE_API_KEY to backend/.env.")
    params = {**params, "apikey": api_key}
    key = tuple(sorted((k, v) for k, v in params.items() if k != "apikey"))
    cached = _cache.get(key)
    if cached and time.time() - cached[0] < ttl:
        return cached[1]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, "Market data is temporarily unavailable. Please try again.")
    if "Note" in data or "Information" in data:
        raise HTTPException(503, "Alpha Vantage rate limit reached. Please try again shortly.")
    if "Error Message" in data:
        raise HTTPException(404, "Cryptocurrency not found by Alpha Vantage.")
    _cache[key] = (time.time(), data)
    return data


async def _daily(symbol: str):
    return await _query({"function":"DIGITAL_CURRENCY_DAILY", "symbol":symbol, "market":"USD"})


def _rows(data):
    rows = data.get("Time Series (Digital Currency Daily)")
    if not rows:
        raise HTTPException(503, "Alpha Vantage returned no daily cryptocurrency data.")
    return rows


def _price_field(row: dict, number: int, label: str) -> float:
    """Read Alpha Vantage's documented `4a. close (USD)` or alternate `4. close` keys."""
    candidates = []
    for key, value in row.items():
        normalized = key.lower()
        if (normalized.startswith(f"{number}.") or normalized.startswith(f"{number}a.")) and label in normalized:
            # Prefer an explicitly USD-denominated field where the response includes both.
            candidates.append(("usd" not in normalized, value))
    if not candidates:
        raise HTTPException(503, f"Alpha Vantage returned incomplete daily data (missing {label}).")
    candidates.sort(key=lambda item: item[0])
    return float(candidates[0][1])


async def search_coins(query: str):
    needle = query.strip().lower()
    return [{"id": symbol.lower(), "name": name, "symbol": symbol, "image": None} for symbol, name in KNOWN_COINS.items() if needle in symbol.lower() or needle in name.lower()][:12]


async def get_coin(coin_id: str):
    symbol = _symbol(coin_id)
    data = await _daily(symbol)
    rows = _rows(data)
    dates = sorted(rows, reverse=True)
    latest, prior = rows[dates[0]], rows[dates[1]] if len(dates) > 1 else None
    close = _price_field(latest, 4, "close")
    prior_close = _price_field(prior, 4, "close") if prior else None
    change = ((close / prior_close) - 1) * 100 if prior_close else None
    meta = data.get("Meta Data", {})
    return {"id":symbol.lower(), "name":KNOWN_COINS.get(symbol, meta.get("2. Digital Currency Name", symbol)), "symbol":symbol, "image":None, "current_price":close, "price_change_percentage_24h":change, "high_24h":_price_field(latest, 2, "high"), "low_24h":_price_field(latest, 3, "low"), "market_cap":None, "total_volume":float(latest.get("5. volume", latest.get("5a. volume", 0)))}


async def get_history(coin_id: str, days: int):
    rows = _rows(await _daily(_symbol(coin_id)))
    prices = []
    for date in sorted(rows)[-days:]:
        timestamp = int(datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
        prices.append([timestamp, _price_field(rows[date], 4, "close")])
    return {"prices": prices}


async def get_markets(per_page=50):
    # Alpha Vantage offers no global market-cap cryptocurrency listing.
    return []
