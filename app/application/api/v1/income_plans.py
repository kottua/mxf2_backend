from app.application.api.depends import file_processing_service_deps, income_plan_service_deps
from app.core.schemas.income_plan_schemas import (
    BulkIncomePlanCreate,
    IncomePlanCreate,
    IncomePlanFileResponse,
    IncomePlanResponse,
    IncomePlanUpdate,
)
from fastapi import APIRouter, UploadFile
from starlette import status

router = APIRouter()


@router.post("/upload/income-plans", response_model=list[IncomePlanFileResponse])
async def upload_premises_specification(
    file: UploadFile,
    file_processing_service: file_processing_service_deps,
) -> list[IncomePlanFileResponse]:
    # Read file content
    file_content = await file.read()

    # Process file using service layer
    premises_data = await file_processing_service.process_income_plan(
        file_content=file_content, filename=file.filename or "unknown"
    )

    return premises_data


@router.post("/bulk", response_model=list[IncomePlanResponse])
async def create_bulk_income_plans(
    request: BulkIncomePlanCreate, income_plan_service: income_plan_service_deps
) -> list[IncomePlanResponse]:
    plans = await income_plan_service.create_bulk_income_plans(request=request)
    return plans


@router.post("/", response_model=IncomePlanResponse)
async def create_income_plan(
    request: IncomePlanCreate, income_plan_service: income_plan_service_deps
) -> IncomePlanResponse:
    plan = await income_plan_service.create(data=request)
    return plan


@router.get("/{id}", response_model=IncomePlanResponse)
async def get_income_plan(id: int, income_plan_service: income_plan_service_deps) -> IncomePlanResponse:
    plan = await income_plan_service.get(id=id)
    return plan


@router.get("/", response_model=list[IncomePlanResponse])
async def get_all_income_plans(income_plan_service: income_plan_service_deps) -> list[IncomePlanResponse]:
    plans = await income_plan_service.get_all()
    return plans


@router.put("/{id}", response_model=IncomePlanResponse)
async def update_income_plan(
    id: int, request: IncomePlanUpdate, income_plan_service: income_plan_service_deps
) -> IncomePlanResponse:
    plan = await income_plan_service.update(id=id, data=request)
    return plan


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income_plan(id: int, income_plan_service: income_plan_service_deps) -> None:
    await income_plan_service.delete(id=id)
