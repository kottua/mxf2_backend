from typing import Sequence

from app.core.interfaces.layout_type_attachment_repository import LayoutTypeAttachmentRepositoryInterface
from app.infrastructure.postgres.models.premises import LayoutTypeAttachment
from app.infrastructure.postgres.session_manager import provide_async_session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class LayoutTypeAttachmentRepository(LayoutTypeAttachmentRepositoryInterface):

    @provide_async_session
    async def create(self, data: dict, session: AsyncSession) -> LayoutTypeAttachment:
        attachment = LayoutTypeAttachment(**data)
        session.add(attachment)
        await session.commit()
        await session.refresh(attachment)
        return attachment

    @provide_async_session
    async def get(self, id: int, session: AsyncSession) -> LayoutTypeAttachment | None:
        result = await session.get(LayoutTypeAttachment, id)
        return result

    @provide_async_session
    async def get_by_reo_id_and_layout_type(
        self, reo_id: int, layout_type: str, session: AsyncSession
    ) -> LayoutTypeAttachment | None:
        result = await session.execute(
            select(LayoutTypeAttachment).where(
                LayoutTypeAttachment.reo_id == reo_id, LayoutTypeAttachment.layout_type == layout_type
            )
        )
        return result.scalar_one_or_none()

    @provide_async_session
    async def get_all_by_reo_id(self, reo_id: int, session: AsyncSession) -> Sequence[LayoutTypeAttachment]:
        result = await session.execute(select(LayoutTypeAttachment).where(LayoutTypeAttachment.reo_id == reo_id))
        attachments = result.scalars().all()
        return attachments

    @provide_async_session
    async def get_all(self, session: AsyncSession) -> Sequence[LayoutTypeAttachment]:
        result = await session.execute(select(LayoutTypeAttachment))
        attachments = result.scalars().all()
        return attachments

    @provide_async_session
    async def update(
        self, attachment: LayoutTypeAttachment, data: dict, session: AsyncSession
    ) -> LayoutTypeAttachment:
        for key, value in data.items():
            setattr(attachment, key, value)
        session.add(attachment)
        await session.commit()
        await session.refresh(attachment)
        return attachment

    @provide_async_session
    async def delete(self, attachment: LayoutTypeAttachment, session: AsyncSession) -> None:
        await session.delete(attachment)
        await session.commit()
