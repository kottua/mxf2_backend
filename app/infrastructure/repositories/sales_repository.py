from typing import Sequence

from app.core.interfaces.sales_repository import SalesRepositoryInterface
from app.infrastructure.postgres.models import Sales
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SalesRepository(SalesRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> Sales:
        sales = Sales(**data)
        session.add(sales)
        await session.commit()
        await session.refresh(sales)
        return sales

    @provide_async_session
    async def get(self, id: int, session: AsyncSession) -> Sales | None:
        result = await session.get(Sales, id)
        return result

    @provide_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[Sales]:
        result = await session.execute(select(Sales))
        sales = result.scalars().all()
        return sales

    @provide_async_session
    async def update(self, sales: Sales, data: dict, session: AsyncSession) -> Sales:
        for key, value in data.items():
            setattr(sales, key, value)
        session.add(sales)
        await session.commit()
        await session.refresh(sales)
        return sales

    @provide_async_session
    async def delete(self, sales: Sales, session: AsyncSession) -> None:
        await session.delete(sales)
        await session.commit()
