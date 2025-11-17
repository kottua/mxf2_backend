from typing import Sequence

from app.core.interfaces.pricing_config_repository import PricingConfigRepositoryInterface
from app.infrastructure.postgres.models import PricingConfig
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class PricingConfigRepository(PricingConfigRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> PricingConfig:
        pricing_config = PricingConfig(**data)
        session.add(pricing_config)
        await session.commit()
        await session.refresh(pricing_config)
        return pricing_config

    @provide_async_session
    async def get(self, config_id: int, session: AsyncSession) -> PricingConfig | None:
        result = await session.get(PricingConfig, config_id)
        return result

    @provide_async_session
    async def get_by_reo_id(self, reo_id: int, session: AsyncSession) -> PricingConfig | None:
        result = await session.execute(
            select(PricingConfig).where(PricingConfig.reo_id == reo_id, PricingConfig.is_active == True)
        )
        config = result.scalar_one_or_none()
        return config

    @provide_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[PricingConfig]:
        result = await session.execute(select(PricingConfig))
        plans = result.scalars().all()
        return plans

    @provide_async_session
    async def update(self, pricing_config: PricingConfig, data: dict, session: AsyncSession) -> PricingConfig:
        for key, value in data.items():
            setattr(pricing_config, key, value)
        session.add(pricing_config)
        await session.commit()
        await session.refresh(pricing_config)
        return pricing_config

    @provide_async_session
    async def delete(self, pricing_config: PricingConfig, session: AsyncSession) -> None:
        await session.delete(pricing_config)
        await session.commit()

    @provide_async_session
    async def deactivate_active_pricing_configs(self, reo_id: int, session: AsyncSession) -> None:
        await session.execute(
            update(PricingConfig)
            .where(PricingConfig.reo_id == reo_id, PricingConfig.is_active == True)
            .values(is_active=False)
        )
