from app.application.api.depends import real_estate_object_service_deps
from app.core.schemas.real_estate_object_schemas import (
    RealEstateObjectCreate,
    RealEstateObjectFullResponse,
    RealEstateObjectResponse,
    RealEstateObjectUpdate,
)
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/", response_model=RealEstateObjectResponse)
async def create_real_estate_object(
    request: RealEstateObjectCreate, real_estate_object_service: real_estate_object_service_deps
) -> RealEstateObjectResponse:
    reo = await real_estate_object_service.create(data=request)
    return reo


@router.get("/{id}", response_model=RealEstateObjectFullResponse)
async def get_real_estate_object(
    id: int, real_estate_object_service: real_estate_object_service_deps
) -> RealEstateObjectFullResponse:
    reo = await real_estate_object_service.get_full(id=id)
    return reo


@router.get("/", response_model=list[RealEstateObjectResponse])
async def get_all_real_estate_objects(
    real_estate_object_service: real_estate_object_service_deps,
) -> list[RealEstateObjectResponse]:
    reos = await real_estate_object_service.get_all()
    return reos


@router.put("/{id}", response_model=RealEstateObjectResponse)
async def update_real_estate_object(
    id: int, request: RealEstateObjectUpdate, real_estate_object_service: real_estate_object_service_deps
) -> RealEstateObjectResponse:
    reo = await real_estate_object_service.update(id=id, data=request)
    return reo


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_real_estate_object(id: int, real_estate_object_service: real_estate_object_service_deps) -> None:
    await real_estate_object_service.delete(id=id)
