from app.application.api.depends import premises_service_deps
from app.core.schemas.premise_schemas import (
    BulkPremisesCreateRequest,
    PremisesCreate,
    PremisesResponse,
    PremisesUpdate,
)
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/bulk", response_model=list[PremisesResponse])
async def create_bulk_premises(request: BulkPremisesCreateRequest, premises_service: premises_service_deps):
    premises = await premises_service.create_bulk_premises(data=request)
    return premises


@router.post("/", response_model=PremisesResponse)
async def create_premises(request: PremisesCreate, premises_service: premises_service_deps):
    premises = await premises_service.create(data=request)
    return premises


@router.get("/{id}", response_model=PremisesResponse)
async def get_premises(id: int, premises_service: premises_service_deps):
    premises = await premises_service.get(id=id)
    return premises


@router.get("/", response_model=list[PremisesResponse])
async def get_all_premises(premises_service: premises_service_deps):
    premises = await premises_service.get_all()
    return premises


@router.put("/{id}", response_model=PremisesResponse)
async def update_premises(id: int, request: PremisesUpdate, premises_service: premises_service_deps):
    premises = await premises_service.update(id=id, data=request)
    return premises


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_premises(id: int, premises_service: premises_service_deps):
    await premises_service.delete(id=id)
    return True
