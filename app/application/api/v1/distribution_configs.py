from app.application.api.depends import current_user_deps, distribution_config_service_deps
from app.core.schemas.distribution_config_schemas import (
    DistributionConfigCreate,
    DistributionConfigResponse,
    DistributionConfigUpdate,
)
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/", response_model=DistributionConfigResponse)
async def create_distribution_config(
    request: DistributionConfigCreate,
    distribution_config_service: distribution_config_service_deps,
    current_user: current_user_deps,
) -> DistributionConfigResponse:
    distribution_config = await distribution_config_service.create(data=request, user=current_user)
    return distribution_config


@router.get("/{id}", response_model=DistributionConfigResponse)
async def get_distribution_config(
    id: int, distribution_config_service: distribution_config_service_deps, current_user: current_user_deps
) -> DistributionConfigResponse:
    config = await distribution_config_service.get(config_id=id, user=current_user)
    return config


@router.get("/", response_model=list[DistributionConfigResponse])
async def get_all_distribution_configs(
    distribution_config_service: distribution_config_service_deps, current_user: current_user_deps
) -> list[DistributionConfigResponse]:
    configs = await distribution_config_service.get_all(user=current_user)
    return configs


@router.put("/{id}", response_model=DistributionConfigResponse)
async def update_distribution_config(
    id: int,
    request: DistributionConfigUpdate,
    distribution_config_service: distribution_config_service_deps,
    current_user: current_user_deps,
) -> DistributionConfigResponse:
    config = await distribution_config_service.update(config_id=id, data=request, user=current_user)
    return config


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_distribution_config(
    id: int, distribution_config_service: distribution_config_service_deps, current_user: current_user_deps
) -> None:
    await distribution_config_service.delete(config_id=id, user=current_user)
