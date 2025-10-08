from app.core.exceptions import ObjectNotFound
from app.core.interfaces.sales_repository import SalesRepositoryInterface
from app.core.schemas.sale_schemas import SalesCreate, SalesResponse


class SalesService:
    def __init__(self, repository: SalesRepositoryInterface):
        self.repository = repository

    async def create(self, data: SalesCreate) -> SalesResponse:
        sales = await self.repository.create(data.model_dump())
        return SalesResponse.model_validate(sales)

    async def get(self, id: int) -> SalesResponse:
        sales = await self.repository.get(id)
        if not sales:
            raise ObjectNotFound(model_name="Sales", id_=id)
        return SalesResponse.model_validate(sales)

    async def get_all(self) -> list[SalesResponse]:
        sales_list = await self.repository.get_all()
        return [SalesResponse.model_validate(sales) for sales in sales_list]

    async def update(self, id: int, data: dict) -> SalesResponse:
        sales = await self.repository.get(id)
        if not sales:
            raise ObjectNotFound(model_name="Sales", id_=id)

        sales = await self.repository.update(sales=sales, data=data)
        return SalesResponse.model_validate(sales)

    async def delete(self, id: int) -> None:
        sales = await self.repository.get(id)
        if not sales:
            raise ObjectNotFound(model_name="Sales", id_=id)

        await self.repository.delete(sales=sales)
