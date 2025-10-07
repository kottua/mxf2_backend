from app.application.api.depends import income_plan_service_deps
from app.core.schemas.income_plan_schemas import (
    BulkIncomePlanCreate,
    IncomePlanCreate,
    IncomePlanResponse,
    IncomePlanUpdate,
)
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/bulk", response_model=list[IncomePlanResponse])
async def create_bulk_income_plans(request: BulkIncomePlanCreate, income_plan_service: income_plan_service_deps):
    plans = await income_plan_service.create_bulk_income_plans(request=request)
    return plans


@router.post("/", response_model=IncomePlanResponse)
async def create_income_plan(request: IncomePlanCreate, income_plan_service: income_plan_service_deps):
    plan = await income_plan_service.create(data=request)
    return plan


@router.get("/{id}", response_model=IncomePlanResponse)
async def get_income_plan(id: int, income_plan_service: income_plan_service_deps):
    plan = await income_plan_service.get(id=id)
    return plan


@router.get("/", response_model=list[IncomePlanResponse])
async def get_all_income_plans(income_plan_service: income_plan_service_deps):
    plans = await income_plan_service.get_all()
    return plans


@router.put("/{id}", response_model=IncomePlanResponse)
async def update_income_plan(id: int, request: IncomePlanUpdate, income_plan_service: income_plan_service_deps):
    plan = await income_plan_service.update(id=id, data=request)
    return plan


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income_plan(id: int, income_plan_service: income_plan_service_deps):
    await income_plan_service.delete(id=id)
