from app.core.exceptions import ObjectNotFound
from app.core.interfaces.distribution_configs_repository import DistributionConfigsRepositoryInterface
from app.core.schemas.distribution_config_schemas import (
    DistributionConfigCreate,
    DistributionConfigResponse,
    DistributionConfigUpdate,
)
from app.core.schemas.user_schemas import UserOutputSchema


class DistributionConfigsService:
    def __init__(self, repository: DistributionConfigsRepositoryInterface):
        self.repository = repository

    async def create(self, data: DistributionConfigCreate, user: UserOutputSchema) -> DistributionConfigResponse:
        distribution_config = await self.repository.create(data.model_dump(), user_id=user.id)
        return DistributionConfigResponse.model_validate(distribution_config)

    async def get(self, config_id: int, user: UserOutputSchema) -> DistributionConfigResponse:
        distribution_config = await self.repository.get(config_id, user_id=user.id)
        if not distribution_config:
            raise ObjectNotFound(model_name="DistributionConfig", id_=config_id)
        return DistributionConfigResponse.model_validate(distribution_config)

    async def update(
        self, config_id: int, data: DistributionConfigUpdate, user: UserOutputSchema
    ) -> DistributionConfigResponse:
        distribution_config = await self.repository.get(config_id, user_id=user.id)
        if not distribution_config:
            raise ObjectNotFound(model_name="DistributionConfig", id_=config_id)

        updated_config = await self.repository.update(distribution_config, data.model_dump(exclude_unset=True))
        return DistributionConfigResponse.model_validate(updated_config)

    async def delete(self, config_id: int, user: UserOutputSchema) -> None:
        distribution_config = await self.repository.get(config_id, user_id=user.id)
        if not distribution_config:
            raise ObjectNotFound(model_name="DistributionConfig", id_=config_id)

        await self.repository.delete(distribution_config)

    async def get_all(self, user: UserOutputSchema) -> list[DistributionConfigResponse]:
        configs = await self.repository.get_all(user_id=user.id)
        return [DistributionConfigResponse.model_validate(config) for config in configs]
