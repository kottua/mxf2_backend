from app.core.exceptions import ObjectNotFound
from app.core.interfaces.distribution_configs_repository import DistributionConfigsRepositoryInterface
from app.core.schemas.distribution_config_schemas import (
    DistributionConfigCreate,
    DistributionConfigResponse,
    DistributionConfigUpdate,
)
from app.core.schemas.user_schemas import UserOutputSchema
from app.core.utils.enums import ConfigStatus


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

    async def create_default_config(self, config_name: str) -> DistributionConfigResponse:
        distribution_config_dto = DistributionConfigCreate(
            func_name=config_name,
            content={"mean1": 0.33, "mean2": 0.67, "stdDev": 0.1, "function_type": "Bimodal"},
            config_status=ConfigStatus.DEFAULT,
        )
        distribution_config = await self.repository.create(distribution_config_dto.model_dump(), user_id=None)
        return DistributionConfigResponse.model_validate(distribution_config)

    async def get_by_name(self, config_name: str) -> DistributionConfigResponse | None:
        distribution_config = await self.repository.get_by_name(config_name)
        if not distribution_config:
            return None
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

    async def get_or_create_base_config(self) -> DistributionConfigResponse:
        """
        Получает или создает базовый distribution config с именем "base_config".

        Args:
            user: Пользователь для создания конфига

        Returns:
            DistributionConfigResponse: Существующий или созданный distribution config
        """
        distribution_config_name = "base_config"
        distribution_config = await self.get_by_name(config_name=distribution_config_name)

        if not distribution_config:
            distribution_config = await self.create_default_config(config_name=distribution_config_name)

        return distribution_config
