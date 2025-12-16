from typing import Sequence

from app.core.interfaces.real_estate_object_repository import RealEstateObjectRepositoryInterface
from app.infrastructure.postgres.models import Premises, PricingConfig, RealEstateObject
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_loader_criteria


class RealEstateObjectRepository(RealEstateObjectRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, user_id: int, session: AsyncSession) -> RealEstateObject:
        reo = RealEstateObject(**data, user_id=user_id)
        session.add(reo)
        await session.commit()
        await session.refresh(reo)
        return reo

    @provide_async_session
    async def get(self, id: int, user_id: int, session: AsyncSession) -> RealEstateObject | None:
        stmt = select(RealEstateObject).where(RealEstateObject.id == id, RealEstateObject.user_id == user_id)
        result = await session.execute(stmt)
        reo = result.scalar_one_or_none()
        return reo

    @provide_async_session
    async def get_by_name(self, name: str, user_id: int, session: AsyncSession) -> RealEstateObject | None:
        stmt = select(RealEstateObject).where(
            RealEstateObject.name == name, RealEstateObject.is_deleted == False, RealEstateObject.user_id == user_id
        )
        result = await session.execute(stmt)
        reo = result.scalar_one_or_none()
        return reo

    @provide_async_session
    async def get_full(self, id: int, user_id: int, session: AsyncSession) -> RealEstateObject | None:
        stmt = (
            select(RealEstateObject)
            .where(RealEstateObject.id == id, RealEstateObject.user_id == user_id)
            .options(
                selectinload(RealEstateObject.premises),
                with_loader_criteria(Premises, Premises.is_active == True),
                selectinload(RealEstateObject.pricing_configs),
                with_loader_criteria(PricingConfig, PricingConfig.is_active == True),
                selectinload(RealEstateObject.committed_prices),
                selectinload(RealEstateObject.income_plans),
                selectinload(RealEstateObject.status_mappings),
                selectinload(RealEstateObject.layout_type_attachments),
            )
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @provide_async_session
    async def get_all(self, user_id: int, session: AsyncSession) -> Sequence[RealEstateObject]:
        stmt = select(RealEstateObject).where(
            RealEstateObject.is_deleted == False, RealEstateObject.user_id == user_id
        )
        result = await session.execute(stmt)
        reos = result.scalars().all()
        return reos

    @provide_async_session
    async def update(self, reo: RealEstateObject, data: dict, session: AsyncSession) -> RealEstateObject:
        for key, value in data.items():
            if value is not None:
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
