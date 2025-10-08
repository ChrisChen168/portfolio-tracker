from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from .. import schemas
from ..models import Asset
from .. import crud


router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("/", response_model=List[schemas.AssetOut])
async def list_all_assets(session: AsyncSession = Depends(get_session)):
    assets = await crud.list_assets(session)
    return [schemas.AssetOut.model_validate(a) for a in assets]


@router.post("/", response_model=schemas.AssetOut)
async def create_asset_endpoint(payload: schemas.AssetCreate, session: AsyncSession = Depends(get_session)):
    asset = Asset(
        name=payload.name,
        symbol=payload.symbol.upper(),
        type=payload.type,
        amount=payload.amount,
        buy_price=payload.buy_price,
        current_price=0.0,
    )
    created = await crud.create_asset(session, asset)
    return schemas.AssetOut.model_validate(created)


@router.put("/{asset_id}", response_model=schemas.AssetOut)
async def update_asset_endpoint(asset_id: int, payload: schemas.AssetUpdate, session: AsyncSession = Depends(get_session)):
    existing = await crud.get_asset(session, asset_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")
    values = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if "symbol" in values:
        values["symbol"] = values["symbol"].upper()
    updated = await crud.update_asset(session, asset_id, values)
    assert updated is not None
    return schemas.AssetOut.model_validate(updated)


@router.delete("/{asset_id}")
async def delete_asset_endpoint(asset_id: int, session: AsyncSession = Depends(get_session)):
    existing = await crud.get_asset(session, asset_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Asset not found")
    await crud.delete_asset_by_id(session, asset_id)
    return {"ok": True}



