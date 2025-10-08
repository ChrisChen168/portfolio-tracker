from __future__ import annotations

from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Asset


async def create_asset(session: AsyncSession, asset: Asset) -> Asset:
    session.add(asset)
    await session.commit()
    await session.refresh(asset)
    return asset


async def list_assets(session: AsyncSession) -> List[Asset]:
    result = await session.execute(select(Asset).order_by(Asset.id))
    return list(result.scalars().all())


async def get_asset(session: AsyncSession, asset_id: int) -> Optional[Asset]:
    result = await session.execute(select(Asset).where(Asset.id == asset_id))
    return result.scalar_one_or_none()


async def update_asset(session: AsyncSession, asset_id: int, values: dict) -> Optional[Asset]:
    await session.execute(update(Asset).where(Asset.id == asset_id).values(**values))
    await session.commit()
    updated = await get_asset(session, asset_id)
    return updated


async def delete_asset_by_id(session: AsyncSession, asset_id: int) -> None:
    await session.execute(delete(Asset).where(Asset.id == asset_id))
    await session.commit()



