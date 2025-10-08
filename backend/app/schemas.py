from __future__ import annotations

from typing import Literal, Optional, List
from pydantic import BaseModel, Field


AssetType = Literal["stock", "crypto", "bond", "cash"]


class AssetBase(BaseModel):
    name: str
    symbol: str
    type: AssetType
    amount: float = Field(ge=0)
    buy_price: float = Field(ge=0)
    current_price: float = Field(ge=0)


class AssetCreate(BaseModel):
    name: str
    symbol: str
    type: AssetType
    amount: float = Field(ge=0)
    buy_price: float = Field(ge=0)


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    type: Optional[AssetType] = None
    amount: Optional[float] = Field(default=None, ge=0)
    buy_price: Optional[float] = Field(default=None, ge=0)
    current_price: Optional[float] = Field(default=None, ge=0)


class AssetOut(AssetBase):
    id: int

    class Config:
        from_attributes = True


class PriceOut(BaseModel):
    symbol: str
    price: float
    source: str


class PortfolioItem(BaseModel):
    asset: AssetOut
    value: float
    pnl: float


class PortfolioOut(BaseModel):
    total_value: float
    items: List[PortfolioItem]


