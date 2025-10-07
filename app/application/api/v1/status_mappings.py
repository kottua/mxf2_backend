from app.application.api.depends import status_mapping_service_deps
from app.core.schemas.status_mapping_schemas import StatusMappingCreate, StatusMappingResponse, StatusMappingUpdate
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/", response_model=StatusMappingResponse)
async def create_status_mapping(request: StatusMappingCreate, status_mapping_service: status_mapping_service_deps):
    status_mapping = await status_mapping_service.create(data=request)
    return status_mapping


@router.get("/{id}", response_model=StatusMappingResponse)
async def get_status_mapping(id: int, status_mapping_service: status_mapping_service_deps):
    status_mapping = await status_mapping_service.get(id=id)
    return status_mapping


@router.get("/", response_model=list[StatusMappingResponse])
async def get_all_status_mappings(status_mapping_service: status_mapping_service_deps):
    status_mappings = await status_mapping_service.get_all()
    return status_mappings


@router.put("/{id}", response_model=StatusMappingResponse)
async def update_status_mapping(
    id: int, request: StatusMappingUpdate, status_mapping_service: status_mapping_service_deps
):
    status_mapping = await status_mapping_service.update(id=id, data=request)
    return status_mapping


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_status_mapping(id: int, status_mapping_service: status_mapping_service_deps):
    await status_mapping_service.delete(id=id)
