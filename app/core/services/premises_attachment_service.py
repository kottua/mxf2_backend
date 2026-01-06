from app.core.exceptions import ObjectNotFound
from app.core.interfaces.layout_type_attachment_repository import PremisesAttachmentRepositoryInterface
from app.core.schemas.premise_schemas import (
    LayoutTypeAttachmentCreate,
    LayoutTypeAttachmentResponse,
    LayoutTypeAttachmentUpdate,
    WindowViewAttachmentCreate,
    WindowViewAttachmentResponse,
    WindowViewAttachmentUpdate,
)


class PremisesAttachmentService:

    def __init__(self, repository: PremisesAttachmentRepositoryInterface):
        self.repository = repository

    async def get(self, id: int) -> LayoutTypeAttachmentResponse:
        attachment = await self.repository.get(id=id)
        if not attachment:
            raise ObjectNotFound(model_name="LayoutTypeAttachment", id_=id)
        return LayoutTypeAttachmentResponse.model_validate(attachment)

    async def get_by_reo_id_and_layout_type(
        self, reo_id: int, layout_type: str
    ) -> LayoutTypeAttachmentResponse | None:
        attachment = await self.repository.get_by_reo_id_and_layout_type(reo_id=reo_id, layout_type=layout_type)
        if not attachment:
            return None
        return LayoutTypeAttachmentResponse.model_validate(attachment)

    async def get_all_by_reo_id(self, reo_id: int) -> list[LayoutTypeAttachmentResponse]:
        attachments = await self.repository.get_all_by_reo_id(reo_id=reo_id)
        return [LayoutTypeAttachmentResponse.model_validate(attachment) for attachment in attachments]

    async def get_all(self) -> list[LayoutTypeAttachmentResponse]:
        attachments = await self.repository.get_all()
        return [LayoutTypeAttachmentResponse.model_validate(attachment) for attachment in attachments]

    async def update(self, id: int, data: LayoutTypeAttachmentUpdate) -> LayoutTypeAttachmentResponse:
        attachment = await self.repository.get(id=id)
        if not attachment:
            raise ObjectNotFound(model_name="LayoutTypeAttachment", id_=id)

        attachment = await self.repository.update(attachment=attachment, data=data.model_dump(exclude_unset=True))
        return LayoutTypeAttachmentResponse.model_validate(attachment)

    async def update_or_create_layout_type(
        self, reo_id: int, layout_type: str, data: LayoutTypeAttachmentCreate
    ) -> LayoutTypeAttachmentResponse:
        """Обновляет существующую запись или создает новую по reo_id и layout_type."""
        existing = await self.repository.get_by_reo_id_and_layout_type(reo_id=reo_id, layout_type=layout_type)
        if existing:
            update_data = LayoutTypeAttachmentUpdate(**data.model_dump())
            attachment = await self.repository.update(
                attachment=existing, data=update_data.model_dump(exclude_unset=True)
            )
        else:
            attachment = await self.repository.create_layout_type(data.model_dump())
        return LayoutTypeAttachmentResponse.model_validate(attachment)

    async def delete_layout_type(self, reo_id: int, layout_type: str) -> None:
        attachment_existing = await self.repository.get_by_reo_id_and_layout_type(
            reo_id=reo_id, layout_type=layout_type
        )
        if not attachment_existing:
            raise ObjectNotFound(model_name="LayoutTypeAttachment", id_=layout_type)

        await self.repository.delete(attachment=attachment_existing)

    async def delete_view_from_window(self, reo_id: int, view_from_window: str) -> None:
        attachment_existing = await self.repository.get_by_reo_id_and_window_view(
            reo_id=reo_id, view_from_window=view_from_window
        )
        if not attachment_existing:
            raise ObjectNotFound(model_name="WindowViewAttachment", id_=view_from_window)

        await self.repository.delete(attachment=attachment_existing)

    async def update_or_create_window_view(
        self, reo_id: int, view_from_window: str, data: WindowViewAttachmentCreate
    ) -> WindowViewAttachmentResponse:
        """Обновляет существующую запись или создает новую по reo_id и view_from_window."""
        existing = await self.repository.get_by_reo_id_and_window_view(
            reo_id=reo_id, view_from_window=view_from_window
        )
        if existing:
            update_data = WindowViewAttachmentUpdate(**data.model_dump())
            attachment = await self.repository.update(
                attachment=existing, data=update_data.model_dump(exclude_unset=True)
            )
        else:
            attachment = await self.repository.create_window_view(data.model_dump())
        return WindowViewAttachmentResponse.model_validate(attachment)
