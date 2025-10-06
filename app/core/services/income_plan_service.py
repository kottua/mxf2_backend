from app.core.exceptions import ValidationException, ObjectNotFound
from app.core.interfaces.income_plans_repository import IncomePlanRepositoryInterface
from app.core.schemas.income_plan_schemas import BulkIncomePlanCreate, IncomePlanResponse, IncomePlanCreate


class IncomePlanService:
    def __init__(self, repository: IncomePlanRepositoryInterface):
        self.repository = repository

    async def create_bulk_income_plans(self, request: BulkIncomePlanCreate) -> list[IncomePlanResponse]:
        active_plans = [plan for plan in request.plans if plan.is_active]

        reo_ids = {plan.reo_id for plan in active_plans}
        if len(reo_ids) > 1:
            raise ValidationException("All active plans must belong to the same REO")

        reo_id = reo_ids.pop()

        reo = await self.repository.get_reo(reo_id=reo_id)
        if not reo:
            raise ObjectNotFound(model_name="RealEstateObject", id_=reo_id)

        income_plans = await self.repository.create_bulk_income_plans(data=request.model_dump(), reo_id=reo.id)
        return [IncomePlanResponse.model_validate(plan) for plan in income_plans]

    async def create(self, data: IncomePlanCreate) -> IncomePlanResponse:
        if data.is_active:
            await self.repository.deactivate_active_plans(reo_id=data.reo_id)

        plan = await self.repository.create(data.model_dump())
        return IncomePlanResponse.model_validate(plan)

    async def get(self, id: int,) -> IncomePlanResponse:
        plan = await self.repository.get(plan_id=id)
        if not plan:
            raise ObjectNotFound(model_name="IncomePlan", id_=id)

        return IncomePlanResponse.model_validate(plan)


    async def get_all(self) -> list[IncomePlanResponse]:
        plans = await self.repository.get_all()
        return [IncomePlanResponse.model_validate(plan) for plan in plans]

    async def update(self, id: int, data: IncomePlanCreate) -> IncomePlanResponse:
        plan = await self.repository.get(plan_id=id)
        if not plan:
            raise ObjectNotFound(model_name="IncomePlan", id_=id)

        if data.is_active:
            await self.repository.deactivate_active_plans(reo_id=data.reo_id)

        plan = await self.repository.update(plan, data.model_dump())

        return IncomePlanResponse.model_validate(plan)

    async def delete(self, id: int) -> None:
        plan = await self.repository.get(plan_id=id)
        if not plan:
            raise ObjectNotFound(model_name="IncomePlan", id_=id)

        await self.repository.delete(plan)