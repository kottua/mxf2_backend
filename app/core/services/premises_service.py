from app.core.exceptions import ObjectNotFound, ValidationException
from app.core.interfaces.premises_repository import PremisesRepositoryInterface
from app.core.interfaces.real_estate_object_repository import RealEstateObjectRepositoryInterface
from app.core.schemas.premise_schemas import (
    BulkPremisesCreateRequest,
    PremisesCreate,
    PremisesResponse,
    PremisesUpdate,
)


class PremisesService:
    def __init__(self, repository: PremisesRepositoryInterface, reo_repository: RealEstateObjectRepositoryInterface):
        self.repository = repository
        self.reo_repository = reo_repository

    async def create_bulk_premises(self, data: BulkPremisesCreateRequest) -> list[PremisesResponse]:
        reo_ids = {premise.reo_id for premise in data.premises}
        if len(reo_ids) > 1:
            raise ValidationException(message="All premises must reference the same RealEstateObject")
        reo_id = reo_ids.pop()
        reo = await self.reo_repository.get(id=reo_id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=reo_id)
        premises_data = [premise.model_dump() for premise in data.premises]

        premises = await self.repository.create_bulk_premises(data=premises_data, reo_id=reo.id)
        return [PremisesResponse.model_validate(premise) for premise in premises]

    async def create(self, data: PremisesCreate) -> PremisesResponse:
        premises = await self.repository.create(data.model_dump())
        return PremisesResponse.model_validate(premises)

    async def get(self, id: int) -> PremisesResponse:
        premises = await self.repository.get(id=id)
        if not premises:
            raise ObjectNotFound(model_name="Premises", id_=id)
        return PremisesResponse.model_validate(premises)

    async def get_all(self) -> list[PremisesResponse]:
        premises_list = await self.repository.get_all()
        return [PremisesResponse.model_validate(premises) for premises in premises_list]

    async def update(self, id: int, data: PremisesUpdate) -> PremisesResponse:
        premises = await self.repository.get(id=id)
        if not premises:
            raise ObjectNotFound(model_name="Premises", id_=id)

        premises = await self.repository.update(premises=premises, data=data.model_dump())
        return PremisesResponse.model_validate(premises)

    async def delete(self, id: int) -> None:
        premises = await self.repository.get(id=id)
        if not premises:
            raise ObjectNotFound(model_name="Premises", id_=id)

        await self.repository.delete(premises=premises)
