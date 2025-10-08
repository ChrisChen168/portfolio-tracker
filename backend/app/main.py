from __future__ import annotations

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from .db import init_db, get_session
from .routers import prices, assets
from . import schemas
from .models import Asset


app = FastAPI(title="Portfolio Tracker API", version="0.1.0")

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


app.include_router(prices.router)
app.include_router(assets.router)


@app.get("/api/portfolio", response_model=schemas.PortfolioOut)
async def get_portfolio(session: AsyncSession = Depends(get_session)):
    from sqlalchemy import select
    result = await session.execute(select(Asset))
    assets_list = list(result.scalars().all())

    items = []
    total_value = 0.0
    for a in assets_list:
        value = (a.current_price or 0.0) * (a.amount or 0.0)
        pnl = (a.current_price - a.buy_price) * a.amount if a.amount and a.current_price is not None else 0.0
        items.append(
            schemas.PortfolioItem(
                asset=schemas.AssetOut.model_validate(a),
                value=value,
                pnl=pnl,
            )
        )
        total_value += value

    return schemas.PortfolioOut(total_value=total_value, items=items)



