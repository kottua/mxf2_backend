from typing import Sequence

from app.core.interfaces.real_estate_object_repository import RealEstateObjectRepositoryInterface
from app.infrastructure.postgres.models import RealEstateObject
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class RealEstateObjectRepository(RealEstateObjectRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> RealEstateObject:
        reo = RealEstateObject(**data)
        session.add(reo)
        await session.commit()
        await session.refresh(reo)
        return reo

    @provide_async_session
    async def get(self, id: int, session: AsyncSession) -> RealEstateObject | None:
        result = await session.get(RealEstateObject, id)
        return result

    @provide_async_session
    async def get_full(self, id: int, session: AsyncSession) -> RealEstateObject | None:
        options = [
            selectinload(RealEstateObject.premises),
            selectinload(RealEstateObject.income_plans),
            selectinload(RealEstateObject.pricing_configs),
        ]
        result = await session.get(RealEstateObject, id, options=options)
        return result

    @provide_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[RealEstateObject]:
        result = await session.execute(select(RealEstateObject).filter_by(is_deleted=False))
        reos = result.scalars().all()
        return reos

    @provide_async_session
    async def update(self, reo: RealEstateObject, data: dict, session: AsyncSession) -> RealEstateObject:
        for key, value in data.items():
            setattr(reo, key, value)
        session.add(reo)
        await session.commit()
        await session.refresh(reo)
        return reo

    @provide_async_session
    async def delete(self, reo: RealEstateObject, session: AsyncSession) -> None:
        reo.is_deleted = True
        session.add(reo)
        await session.commit()
