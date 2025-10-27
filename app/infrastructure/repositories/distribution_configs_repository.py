from typing import Sequence

from app.core.interfaces.distribution_configs_repository import DistributionConfigsRepositoryInterface
from app.infrastructure.postgres.models import DistributionConfig
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DistributionConfigsRepository(DistributionConfigsRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, user_id: int, session: AsyncSession) -> DistributionConfig:
        config = DistributionConfig(**data, user_id=user_id)
        session.add(config)
        await session.commit()
        await session.refresh(config)
        return config

    @provide_async_session
    async def get(self, config_id: int, user_id: int, session: AsyncSession) -> DistributionConfig | None:
        stmt = select(DistributionConfig).where(
            DistributionConfig.id == config_id, DistributionConfig.user_id == user_id
        )
        result = await session.execute(stmt)
        reo = result.scalar_one_or_none()
        return reo

    @provide_async_session
    async def update(self, config: DistributionConfig, data: dict, session: AsyncSession) -> DistributionConfig | None:
        for key, value in data.items():
            if value is not None:
                setattr(config, key, value)
        session.add(config)
        await session.commit()
        await session.refresh(config)
        return config

    @provide_async_session
    async def delete(self, config: DistributionConfig, session: AsyncSession) -> None:
        await session.delete(config)
        await session.commit()

    @provide_async_session
    async def get_all(self, user_id: int, session: AsyncSession) -> Sequence[DistributionConfig]:
        stmt = select(DistributionConfig).where(DistributionConfig.user_id == user_id)
        result = await session.execute(stmt)
        configs = result.scalars().all()
        return configs
