from app.application.api.depends import current_user_deps, scoring_service_deps
from app.core.schemas.calculation_schemas import RealEstateObjectWithCalculations
from fastapi import APIRouter

router = APIRouter()


@router.get("/scoring/{reo_id}/{distribution_config_id}", response_model=RealEstateObjectWithCalculations)
async def calculate_scoring(
    reo_id: int, distribution_config_id: int, scoring_service: scoring_service_deps, current_user: current_user_deps
) -> RealEstateObjectWithCalculations:
    result = await scoring_service.calculate_scoring(
        reo_id=reo_id, distribution_config_id=distribution_config_id, user=current_user
    )
    return result
