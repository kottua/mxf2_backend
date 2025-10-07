from typing import Sequence

from app.core.interfaces.premises_repository import PremisesRepositoryInterface
from app.infrastructure.postgres.models import Premises
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession


class PremisesRepository(PremisesRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> Premises:
        premises = Premises(**data)
        session.add(premises)
        await session.commit()
        await session.refresh(premises)
        return premises

    @provide_async_session
    async def get(self, id: int, session: AsyncSession) -> Premises | None:
        result = await session.get(Premises, id)
        return result

    @provide_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[Premises]:
        result = await session.execute(select(Premises))
        premises = result.scalars().all()
        return premises

    @provide_async_session
    async def update(self, premises: Premises, data: dict, session: AsyncSession) -> Premises:
        for key, value in data.items():
            setattr(premises, key, value)
        session.add(premises)
        await session.commit()
        await session.refresh(premises)
        return premises

    @provide_async_session
    async def delete(self, premises: Premises, session: AsyncSession) -> None:
        await session.delete(premises)
        await session.commit()

    @provide_async_session
    async def fetch_recent_premises(self, reo_id: int, limit: int, session: AsyncSession) -> Sequence[Premises]:
        result = await session.execute(
            select(Premises).where(Premises.reo_id == reo_id).order_by(Premises.id.desc()).limit(limit)
        )
        created_premises = result.scalars().all()
        return created_premises

    @provide_async_session
    async def create_bulk_premises(self, data: list[dict], reo_id: int, session: AsyncSession) -> Sequence[Premises]:
        stmt = insert(Premises)
        await session.execute(stmt, data)
        await session.commit()
        result = await self.fetch_recent_premises(reo_id=reo_id, limit=len(data), session=session)
        return result
