from app.core.exceptions import ObjectAlreadyExists, ObjectNotFound
from app.core.interfaces.real_estate_object_repository import RealEstateObjectRepositoryInterface
from app.core.schemas.real_estate_object_schemas import (
    RealEstateObjectCreate,
    RealEstateObjectFullResponse,
    RealEstateObjectResponse,
    RealEstateObjectUpdate,
)


class RealEstateObjectService:
    def __init__(self, repository: RealEstateObjectRepositoryInterface):
        self.repository = repository

    async def create(self, data: RealEstateObjectCreate) -> RealEstateObjectResponse:
        reo = await self.get_by_name(name=data.name)
        if reo:
            raise ObjectAlreadyExists(message="Real Estate with this name already exists")

        reo = await self.repository.create(data.model_dump())
        return RealEstateObjectResponse.model_validate(reo)

    async def get_full(self, id: int) -> RealEstateObjectFullResponse:
        reo = await self.repository.get_full(id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=id)

        return RealEstateObjectFullResponse.model_validate(reo)

    async def get_all(self) -> list[RealEstateObjectResponse]:
        reos = await self.repository.get_all()
        return [RealEstateObjectResponse.model_validate(reo) for reo in reos]

    async def get_by_name(self, name: str) -> RealEstateObjectResponse | None:
        reo = await self.repository.get_by_name(name)
        if not reo:
            return None

        return RealEstateObjectResponse.model_validate(reo)

    async def get(self, id: int) -> RealEstateObjectResponse:
        reo = await self.repository.get(id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=id)

        return RealEstateObjectResponse.model_validate(reo)

    async def update(self, id: int, data: RealEstateObjectUpdate) -> RealEstateObjectResponse:
        reo = await self.repository.get(id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=id)

        reo = await self.repository.update(reo=reo, data=data.model_dump())
        return RealEstateObjectResponse.model_validate(reo)

    async def delete(self, id: int) -> None:
        reo = await self.repository.get(id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=id)

        await self.repository.delete(reo=reo)
