from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.interfaces.distribution_configs_repository import DistributionConfigsRepositoryInterface
from app.infrastructure.postgres.models import DistributionConfig
from app.infrastructure.postgres.session_manager import provide_async_session


class DistributionConfigsRepository(DistributionConfigsRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> DistributionConfig:
        config = DistributionConfig(**data )
        session.add(config)
        await session.commit()
        await session.refresh(config)
        return config

    @provide_async_session
    async def get(self, config_id: int, session: AsyncSession) -> DistributionConfig | None:
        result = await session.get(DistributionConfig, config_id)
        return result

    @provide_async_session
    async def update(self, config: DistributionConfig, data: dict, session: AsyncSession) -> DistributionConfig | None:
        for key, value in data.items():
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
    async def get_all(self, session: AsyncSession) -> Sequence[DistributionConfig]:
        result = await session.execute(select(DistributionConfig))
        return result.scalars().all()
