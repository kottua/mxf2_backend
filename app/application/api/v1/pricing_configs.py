from app.application.api.depends import current_user_deps, pricing_config_service_deps
from app.core.schemas.pricing_config_schemas import PricingConfigCreate, PricingConfigResponse, PricingConfigUpdate
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/", response_model=PricingConfigResponse)
async def create_pricing_config(
    request: PricingConfigCreate, pricing_config_service: pricing_config_service_deps, _: current_user_deps
) -> PricingConfigResponse:
    config = await pricing_config_service.create_pricing_config(data=request)
    return config


@router.get("/{reo_id}", response_model=PricingConfigResponse)
async def get_pricing_config(
    reo_id: int, pricing_config_service: pricing_config_service_deps, _: current_user_deps
) -> PricingConfigResponse:
    config = await pricing_config_service.get_pricing_config(reo_id=reo_id)
    return config


@router.get("/", response_model=list[PricingConfigResponse])
async def get_all_pricing_configs(
    pricing_config_service: pricing_config_service_deps, _: current_user_deps
) -> list[PricingConfigResponse]:
    configs = await pricing_config_service.get_all_pricing_configs()
    return configs


@router.put("/{id}", response_model=PricingConfigResponse)
async def update_pricing_config(
    id: int, request: PricingConfigUpdate, pricing_config_service: pricing_config_service_deps, _: current_user_deps
) -> PricingConfigResponse:
    config = await pricing_config_service.update_pricing_config(config_id=id, data=request)
    return config


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pricing_config(
    id: int, pricing_config_service: pricing_config_service_deps, _: current_user_deps
) -> None:
    await pricing_config_service.delete_pricing_config(plan_id=id)
