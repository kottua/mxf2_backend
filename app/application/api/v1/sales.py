from app.application.api.depends import current_user_deps, sales_service_deps
from app.core.schemas.sale_schemas import SalesCreate, SalesResponse, SalesUpdate
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/", response_model=SalesResponse)
async def create_sale(request: SalesCreate, sales_service: sales_service_deps, _: current_user_deps) -> SalesResponse:
    sale = await sales_service.create(request)
    return sale


@router.get("/{id}", response_model=SalesResponse)
async def get_sale(id: int, sales_service: sales_service_deps, _: current_user_deps) -> SalesResponse:
    sale = await sales_service.get(id)
    return sale


@router.get("/", response_model=list[SalesResponse])
async def get_all_sales(sales_service: sales_service_deps, _: current_user_deps) -> list[SalesResponse]:
    sales = await sales_service.get_all()
    return sales


@router.put("/{id}", response_model=SalesResponse)
async def update_sale(
    id: int, request: SalesUpdate, sales_service: sales_service_deps, _: current_user_deps
) -> SalesResponse:
    sale = await sales_service.update(id, request)
    return sale


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sale(id: int, sales_service: sales_service_deps, _: current_user_deps) -> None:
    await sales_service.delete(id)
