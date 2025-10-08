from app.application.api.depends import file_processing_service_deps, premises_service_deps
from app.core.schemas.premise_schemas import (
    BulkPremisesCreateRequest,
    PremisesCreate,
    PremisesFileSpecificationResponse,
    PremisesResponse,
    PremisesUpdate,
)
from fastapi import APIRouter, UploadFile
from starlette import status

router = APIRouter()


@router.post("/upload/specification", response_model=list[PremisesFileSpecificationResponse])
async def upload_premises_specification(
    file: UploadFile,
    file_processing_service: file_processing_service_deps,
) -> list[PremisesFileSpecificationResponse]:
    # Read file content
    file_content = await file.read()

    # Process file using service layer
    premises_data = await file_processing_service.process_specification(
        file_content=file_content, filename=file.filename or "unknown"
    )

    return premises_data


@router.post("/bulk", response_model=list[PremisesResponse])
async def create_bulk_premises(
    request: BulkPremisesCreateRequest, premises_service: premises_service_deps
) -> list[PremisesResponse]:
    premises = await premises_service.create_bulk_premises(data=request)
    return premises


@router.post("/", response_model=PremisesResponse)
async def create_premises(request: PremisesCreate, premises_service: premises_service_deps) -> PremisesResponse:
    premises = await premises_service.create(data=request)
    return premises


@router.get("/{id}", response_model=PremisesResponse)
async def get_premises(id: int, premises_service: premises_service_deps) -> PremisesResponse:
    premises = await premises_service.get(id=id)
    return premises


@router.get("/", response_model=list[PremisesResponse])
async def get_all_premises(premises_service: premises_service_deps) -> list[PremisesResponse]:
    premises = await premises_service.get_all()
    return premises


@router.put("/{id}", response_model=PremisesResponse)
async def update_premises(
    id: int, request: PremisesUpdate, premises_service: premises_service_deps
) -> PremisesResponse:
    premises = await premises_service.update(id=id, data=request)
    return premises


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_premises(id: int, premises_service: premises_service_deps) -> None:
    await premises_service.delete(id=id)
