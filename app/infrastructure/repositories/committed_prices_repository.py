from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from app.core.interfaces.committed_prices_repository import CommittedPricesRepositoryInterface
from app.infrastructure.postgres.models import CommittedPrices, DistributionConfig, PricingConfig, RealEstateObject
from app.infrastructure.postgres.session_manager import provide_async_session


class CommittedPricesRepository(CommittedPricesRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> CommittedPrices:
        price = CommittedPrices(**data)
        session.add(price)
        await session.commit()
        await session.refresh(price)
        return price

    @provide_async_session
    async def get(self, id: int, session: AsyncSession) -> CommittedPrices | None:
        result = await session.get(CommittedPrices, id)
        return result

    @provide_async_session
    async def get_all_committed_prices(self, session: AsyncSession) -> Sequence[CommittedPrices]:
        result = await session.execute(select(CommittedPrices))
        return result.scalars().all()

    @provide_async_session
    async def deactivate_active_prices(self, reo_id: int, session: AsyncSession) -> None:
        await session.execute(
            update(CommittedPrices)
            .where(
                CommittedPrices.reo_id == reo_id,
                CommittedPrices.is_active == True
            )
            .values(is_active=False)
        )

    @provide_async_session
    async def exists_distribution_config(self, config_id: int, session: AsyncSession) -> bool:
        result = await session.execute(
            select(DistributionConfig.id).where(DistributionConfig.id == config_id)
        )
        return result.scalar_one_or_none() is not None

    @provide_async_session
    async def exists_pricing_config(self, config_id: int, session: AsyncSession) -> bool:
        result = await session.execute(
            select(PricingConfig.id).where(DistributionConfig.id == config_id)
        )
        return result.scalar_one_or_none() is not None

    @provide_async_session
    async def exists_reo_id(self, reo_id: int, session: AsyncSession) -> bool:
        result = await session.execute(
            select(RealEstateObject.id).where(DistributionConfig.id == reo_id)
        )
        return result.scalar_one_or_none() is not None