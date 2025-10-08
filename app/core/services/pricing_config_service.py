from app.core.exceptions import ObjectNotFound
from app.core.interfaces.pricing_config_repository import PricingConfigRepositoryInterface
from app.core.schemas.pricing_config_schemas import PricingConfigCreate, PricingConfigResponse


class PricingConfigService:
    def __init__(self, repository: PricingConfigRepositoryInterface):
        self.repository = repository

    async def create_pricing_config(self, data: PricingConfigCreate) -> PricingConfigResponse:
        if data.is_active:
            await self.repository.deactivate_active_pricing_configs(reo_id=data.reo_id)

        pricing_config = await self.repository.create(data=data.model_dump())
        return PricingConfigResponse.model_validate(pricing_config)

    async def get_pricing_config(self, reo_id: int) -> PricingConfigResponse:
        pricing_config = await self.repository.get_by_reo_id(reo_id=reo_id)
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=reo_id)

        return PricingConfigResponse.model_validate(pricing_config)

    async def get_all_pricing_configs(self) -> list[PricingConfigResponse]:
        pricing_configs = await self.repository.get_all()
        return [PricingConfigResponse.model_validate(config) for config in pricing_configs]

    async def update_pricing_config(self, config_id: int, data: PricingConfigCreate) -> PricingConfigResponse:
        pricing_config = await self.repository.get(config_id=config_id)
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=config_id)

        pricing_config = await self.repository.update(pricing_config, data.model_dump())
        return PricingConfigResponse.model_validate(pricing_config)

    async def delete_pricing_config(self, config_id: int) -> None:
        pricing_config = await self.repository.get(config_id=config_id)
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=config_id)

        await self.repository.delete(pricing_config=pricing_config)
