from app.application.api.depends import current_user_deps, file_processing_service_deps, premises_service_deps
from app.core.schemas.premise_schemas import (
    BulkPremisesCreateRequest,
    PremisesCreate,
    PremisesFileSpecificationResponse,
    PremisesResponse,
    PremisesUpdate,
)
from fastapi import APIRouter, UploadFile
from starlette import status
from starlette.responses import Response

router = APIRouter()


@router.post("/upload/specification/{reo_id}", response_model=list[PremisesFileSpecificationResponse])
async def upload_premises_specification(
    reo_id: int,
    file: UploadFile,
    file_processing_service: file_processing_service_deps,
    premises_service: premises_service_deps,
    current_user: current_user_deps,
) -> list[PremisesFileSpecificationResponse]:
    # Read file content
    file_content = await file.read()

    # Process file using service layer
    premises_data = await file_processing_service.process_specification(
        file_content=file_content, filename=file.filename or "unknown"
    )
    premises_create_list = []
    for spec in premises_data:
        spec_dict = spec.model_dump(by_alias=False)
        # Convert entrance from int to str
        if isinstance(spec_dict.get("entrance"), int):
            spec_dict["entrance"] = str(spec_dict["entrance"])
        # Add reo_id from endpoint parameter
        spec_dict["reo_id"] = reo_id

        premises_create_list.append(PremisesCreate(**spec_dict))

    bulk_request = BulkPremisesCreateRequest(premises=premises_create_list)
    await premises_service.create_bulk_premises(data=bulk_request, user=current_user)

    return premises_data


@router.post("/bulk", response_model=list[PremisesResponse])
async def create_bulk_premises(
    request: BulkPremisesCreateRequest, premises_service: premises_service_deps, current_user: current_user_deps
) -> list[PremisesResponse]:
    premises = await premises_service.create_bulk_premises(data=request, user=current_user)
    return premises


@router.post("/", response_model=PremisesResponse)
async def create_premises(
    request: PremisesCreate, premises_service: premises_service_deps, _: current_user_deps
) -> PremisesResponse:
    premises = await premises_service.create(data=request)
    return premises


@router.get("/{id}", response_model=PremisesResponse)
async def get_premises(id: int, premises_service: premises_service_deps, _: current_user_deps) -> PremisesResponse:
    premises = await premises_service.get(id=id)
    return premises


@router.get("/", response_model=list[PremisesResponse])
async def get_all_premises(premises_service: premises_service_deps, _: current_user_deps) -> list[PremisesResponse]:
    premises = await premises_service.get_all()
    return premises


@router.put("/{id}", response_model=PremisesResponse)
async def update_premises(
    id: int, request: PremisesUpdate, premises_service: premises_service_deps, _: current_user_deps
) -> PremisesResponse:
    premises = await premises_service.update(id=id, data=request)
    return premises


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_premises(id: int, premises_service: premises_service_deps, _: current_user_deps) -> None:
    await premises_service.delete(id=id)


@router.get("/download/excel/{reo_id}/{distribution_config_id}")
async def download_premises_excel_with_actual_price(
    reo_id: int,
    distribution_config_id: int,
    file_processing_service: file_processing_service_deps,
    # _: current_user_deps,
) -> Response:
    """
    Download Excel file with premises data and actual_price_per_sqm from committed prices.

    Args:
        reo_id: Real estate object ID
        distribution_config_id: Distribution config ID

    Returns:
        Excel file as downloadable response
    """
    excel_bytes = await file_processing_service.generate_excel_with_actual_price(
        reo_id=reo_id, distribution_config_id=distribution_config_id
    )

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=premises_with_actual_price_reo_{reo_id}_dist_{distribution_config_id}.xlsx"
        },
    )
