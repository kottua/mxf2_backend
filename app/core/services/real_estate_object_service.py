from app.core.exceptions import ObjectAlreadyExists, ObjectNotFound
from app.core.interfaces.real_estate_object_repository import RealEstateObjectRepositoryInterface
from app.core.schemas.real_estate_object_schemas import (
    RealEstateObjectCreate,
    RealEstateObjectFullResponse,
    RealEstateObjectResponse,
    RealEstateObjectUpdate,
)
from app.core.schemas.user_schemas import UserOutputSchema


class RealEstateObjectService:
    def __init__(self, repository: RealEstateObjectRepositoryInterface):
        self.repository = repository

    async def create(self, data: RealEstateObjectCreate, user: UserOutputSchema) -> RealEstateObjectResponse:
        reo = await self.get_by_name(name=data.name, user_id=user.id)
        if reo:
            raise ObjectAlreadyExists(message="Real Estate with this name already exists")

        reo = await self.repository.create(data.model_dump(), user_id=user.id)
        return RealEstateObjectResponse.model_validate(reo)

    async def get_full(self, id: int, user: UserOutputSchema) -> RealEstateObjectFullResponse:
        reo = await self.repository.get_full(id, user_id=user.id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=id)

        return RealEstateObjectFullResponse.model_validate(reo)

    async def get_all(self, user: UserOutputSchema) -> list[RealEstateObjectResponse]:
        reos = await self.repository.get_all(user_id=user.id)
        return [RealEstateObjectResponse.model_validate(reo) for reo in reos]

    async def get_by_name(self, name: str, user_id: int) -> RealEstateObjectResponse | None:
        reo = await self.repository.get_by_name(name, user_id=user_id)
        if not reo:
            return None

        return RealEstateObjectResponse.model_validate(reo)

    async def update(self, id: int, data: RealEstateObjectUpdate, user: UserOutputSchema) -> RealEstateObjectResponse:
        reo = await self.repository.get(id, user_id=user.id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=id)

        reo = await self.repository.update(reo=reo, data=data.model_dump())
        return RealEstateObjectResponse.model_validate(reo)

    async def delete(self, id: int, user: UserOutputSchema) -> None:
        reo = await self.repository.get(id, user_id=user.id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=id)

        await self.repository.delete(reo=reo)
