from __future__ import annotations

from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # stock/crypto/bond/cash
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    buy_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)



