from typing import Dict, Tuple
from uuid import UUID

from app.core.interfaces.user_repository import UserRepositoryInterface
from app.infrastructure.postgres.models.users import ApiKey, User
from app.infrastructure.postgres.session_manager import provide_async_session
from pydantic import EmailStr
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository(UserRepositoryInterface):

    @provide_async_session
    async def create(self, user_payload: dict, session: AsyncSession) -> User:
        user = User(**user_payload)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @provide_async_session
    async def get(self, email: EmailStr, session: AsyncSession) -> User | None:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @provide_async_session
    async def get_by_id(self, user_id: UUID, session: AsyncSession) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @provide_async_session
    async def get_all(self, limit: int, offset: int, session: AsyncSession) -> Tuple[list[User], int]:
        count_query = select(func.count(User.id))
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        query = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(query)
        users = result.scalars().all()
        return list(users), total

    @provide_async_session
    async def update(self, user: User, updates: Dict, session: AsyncSession) -> User:
        user = await session.merge(user)
        for key, value in updates.items():
            if value is not None:
                setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user

    @provide_async_session
    async def delete(self, user: User, session: AsyncSession) -> None:
        await session.delete(user)
        await session.commit()

    @provide_async_session
    async def update_password(self, user: User, new_password: str, session: AsyncSession) -> None:
        user = await session.merge(user)
        user.password = new_password
        await session.commit()

    @provide_async_session
    async def create_api_key(self, payload: dict, user: User, session: AsyncSession) -> ApiKey:
        api_key = ApiKey(**payload, user=user)
        session.add(api_key)
        await session.commit()
        await session.refresh(api_key)
        return api_key
