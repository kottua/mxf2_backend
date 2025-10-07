from app.core.exceptions import ObjectNotFound
from app.core.interfaces.status_mapping_repository import StatusMappingRepositoryInterface
from app.core.schemas.status_mapping_schemas import StatusMappingCreate, StatusMappingResponse, StatusMappingUpdate


class StatusMappingService:

    def __init__(self, repository: StatusMappingRepositoryInterface):
        self.repository = repository

    async def create(self, data: StatusMappingCreate) -> StatusMappingResponse:
        status_mapping = await self.repository.create(data.model_dump())
        return StatusMappingResponse.model_validate(status_mapping)

    async def get(self, id: int) -> StatusMappingResponse:
        status_mapping = await self.repository.get(id)
        if not status_mapping:
            raise ObjectNotFound(model_name="StatusMapping", id_=id)
        return StatusMappingResponse.model_validate(status_mapping)

    async def get_all(self) -> list[StatusMappingResponse]:
        status_mappings = await self.repository.get_all()
        return [StatusMappingResponse.model_validate(status_mapping) for status_mapping in status_mappings]

    async def update(self, id: int, data: StatusMappingUpdate) -> StatusMappingResponse:
        status_mapping = await self.repository.get(id=id)
        if not status_mapping:
            raise ObjectNotFound(model_name="StatusMapping", id_=id)

        updated_status_mapping = await self.repository.update(status_mapping, data.model_dump())
        return StatusMappingResponse.model_validate(updated_status_mapping)

    async def delete(self, id: int) -> None:
        status_mapping = await self.repository.get(id=id)
        if not status_mapping:
            raise ObjectNotFound(model_name="StatusMapping", id_=id)

        await self.repository.delete(status_mapping)
