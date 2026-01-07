from app.core.interfaces.api_repository_repository import ApiRepositoryInterface
from app.infrastructure.postgres.models.users import ApiKey
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ApiKeyRepository(ApiRepositoryInterface):

    @provide_async_session
    async def get_by_user_id(self, user_id: int, session: AsyncSession) -> ApiKey | None:
        res = await session.execute(select(ApiKey).where(ApiKey.user_id == user_id))
        return res.scalar_one_or_none()

    @provide_async_session
    async def delete_by_user_id(self, user_id: int, session: AsyncSession) -> None:
        api_key = await self.get_by_user_id(user_id=user_id, session=session)
        if api_key:
            await session.delete(api_key)
            await session.commit()
