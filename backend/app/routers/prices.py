from __future__ import annotations

import os
from fastapi import APIRouter, HTTPException
import httpx

from ..schemas import PriceOut


router = APIRouter(prefix="/api/price", tags=["price"])


YF_BASE = "https://query1.finance.yahoo.com/v7/finance/quote"
COINGECKO_BASE = os.getenv("COINGECKO_BASE", "https://api.coingecko.com/api/v3")


@router.get("/stock/{symbol}", response_model=PriceOut)
async def get_stock_price(symbol: str) -> PriceOut:
    params = {"symbols": symbol}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(YF_BASE, params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch stock price")
        data = r.json()
        try:
            quote = data["quoteResponse"]["result"][0]
            price = float(quote.get("regularMarketPrice"))
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=404, detail="Symbol not found") from exc
    return PriceOut(symbol=symbol.upper(), price=price, source="yahoo_finance")


@router.get("/crypto/{symbol}", response_model=PriceOut)
async def get_crypto_price(symbol: str) -> PriceOut:
    # CoinGecko simple price expects ids, but also supports symbol mapping via /coins/list. For simplicity
    # attempt direct by symbol in vs_currency=usd through markets endpoint.
    params = {"vs_currency": "usd", "ids": "", "symbols": symbol.lower(), "per_page": 1, "page": 1}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{COINGECKO_BASE}/coins/markets", params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch crypto price")
        arr = r.json()
        if not arr:
            raise HTTPException(status_code=404, detail="Crypto symbol not found")
        price = float(arr[0]["current_price"])  # USD
        normalized_symbol = arr[0]["symbol"].upper()
    return PriceOut(symbol=normalized_symbol, price=price, source="coingecko")


@router.get("/bond/{symbol}", response_model=PriceOut)
async def get_bond_price(symbol: str) -> PriceOut:
    # Placeholder: allow static/mock input via env: BOND_{SYMBOL}_PRICE
    env_key = f"BOND_{symbol.upper()}_PRICE"
    price_str = os.getenv(env_key)
    if price_str is None:
        # basic default mock
        price = 100.0
    else:
        try:
            price = float(price_str)
        except ValueError as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail="Invalid mock price in env") from exc
    return PriceOut(symbol=symbol.upper(), price=price, source="mock")


@router.get("/cash/{currency}", response_model=PriceOut)
async def get_cash_fx(currency: str) -> PriceOut:
    # Simple FX via Yahoo Finance converting 1 unit to USD, e.g., EURUSD=X
    if currency.lower() == "usd":
        return PriceOut(symbol="USD", price=1.0, source="static")
    pair = f"{currency.upper()}USD=X"
    params = {"symbols": pair}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(YF_BASE, params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch FX rate")
        data = r.json()
        try:
            quote = data["quoteResponse"]["result"][0]
            price = float(quote.get("regularMarketPrice"))
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=404, detail="Currency not found") from exc
    return PriceOut(symbol=currency.upper(), price=price, source="yahoo_finance")



