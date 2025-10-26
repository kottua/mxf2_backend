from typing import Sequence

from app.core.interfaces.real_estate_object_repository import RealEstateObjectRepositoryInterface
from app.infrastructure.postgres.models import Premises, PricingConfig, RealEstateObject
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria


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
    async def get_by_name(self, name: str, session: AsyncSession) -> RealEstateObject | None:
        result = await session.execute(select(RealEstateObject).filter_by(name=name, is_deleted=False))
        reo = result.scalars().first()
        return reo

    @provide_async_session
    async def get_full(self, id: int, session: AsyncSession) -> RealEstateObject | None:
        options = [
            selectinload(RealEstateObject.premises),
            with_loader_criteria(Premises, Premises.is_active == True),
            selectinload(RealEstateObject.pricing_configs),
            with_loader_criteria(PricingConfig, PricingConfig.is_active == True),
            selectinload(RealEstateObject.committed_prices),
            selectinload(RealEstateObject.income_plans),
            selectinload(RealEstateObject.status_mappings),
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
