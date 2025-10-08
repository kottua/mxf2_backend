from typing import Sequence

from app.core.interfaces.income_plans_repository import IncomePlanRepositoryInterface
from app.infrastructure.postgres.models import IncomePlan
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class IncomePlanRepository(IncomePlanRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> IncomePlan:
        plan = IncomePlan(**data)
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
        return plan

    @provide_async_session
    async def get(self, plan_id: int, session: AsyncSession) -> IncomePlan | None:
        result = await session.get(IncomePlan, plan_id)
        return result

    @provide_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[IncomePlan]:
        result = await session.execute(
            select(IncomePlan).order_by(IncomePlan.uploaded_at.desc()).filter_by(is_deleted=False)
        )
        plans = result.scalars().all()
        return plans

    @provide_async_session
    async def update(self, plan: IncomePlan, data: dict, session: AsyncSession) -> IncomePlan:
        for key, value in data.items():
            setattr(plan, key, value)
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
        return plan

    @provide_async_session
    async def delete(self, plan: IncomePlan, session: AsyncSession) -> None:
        await session.delete(plan)
        await session.commit()

    @provide_async_session
    async def create_bulk_income_plans(
        self, reo_id: int, data: list[dict], session: AsyncSession
    ) -> Sequence[IncomePlan]:
        stmt = insert(IncomePlan)
        await session.execute(stmt, data)
        await session.commit()
        result = await session.execute(
            select(IncomePlan).where(IncomePlan.reo_id == reo_id).order_by(IncomePlan.uploaded_at.desc())
        )
        created_plans = result.scalars().all()
        return created_plans

    @provide_async_session
    async def deactivate_active_plans(self, reo_id: int, session: AsyncSession) -> None:
        await session.execute(
            update(IncomePlan).where(IncomePlan.reo_id == reo_id, IncomePlan.is_active == True).values(is_active=False)
        )
