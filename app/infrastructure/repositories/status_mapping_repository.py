from typing import Sequence

from app.core.interfaces.status_mapping_repository import StatusMappingRepositoryInterface
from app.infrastructure.postgres.models import StatusMapping
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class StatusMappingRepository(StatusMappingRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> StatusMapping:
        status_mapping = StatusMapping(**data)
        session.add(status_mapping)
        await session.commit()
        await session.refresh(status_mapping)
        return status_mapping

    @provide_async_session
    async def get(self, id: int, session: AsyncSession) -> StatusMapping | None:
        result = await session.get(StatusMapping, id)
        return result

    @provide_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[StatusMapping]:
        result = await session.execute(select(StatusMapping))
        return result.scalars().all()

    @provide_async_session
    async def update(self, status_mapping: StatusMapping, data: dict, session: AsyncSession) -> StatusMapping:
        for key, value in data.items():
            setattr(status_mapping, key, value)
        session.add(status_mapping)
        await session.commit()
        await session.refresh(status_mapping)
        return status_mapping

    @provide_async_session
    async def delete(self, status_mapping: StatusMapping, session: AsyncSession) -> None:
        await session.delete(status_mapping)
        await session.commit()
