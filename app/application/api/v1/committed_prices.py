from typing import List

from app.application.api.depends import committed_service_deps
from app.core.schemas.committed_price_schemas import CommittedPricesCreate, CommittedPricesResponse
from fastapi import APIRouter

router = APIRouter()


@router.post("/", response_model=CommittedPricesResponse)
async def create_committed_price(
    request: CommittedPricesCreate, committed_service: committed_service_deps
) -> CommittedPricesResponse:
    price = await committed_service.create_committed_price(data=request)
    return price


@router.get("/{id}", response_model=CommittedPricesResponse)
async def get_committed_price(id: int, committed_service: committed_service_deps) -> CommittedPricesResponse:
    price = await committed_service.get_committed_price(id=id)
    return price


@router.get("/", response_model=List[CommittedPricesResponse])
async def get_all_committed_prices(committed_service: committed_service_deps) -> List[CommittedPricesResponse]:
    prices = await committed_service.get_all_committed_prices()
    return prices
