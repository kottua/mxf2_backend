import copy

from app.core.exceptions import ObjectNotFound
from app.core.interfaces.pricing_config_repository import PricingConfigRepositoryInterface
from app.core.schemas.pricing_config_schemas import (
    PricingConfigCreate,
    PricingConfigResponse,
    PricingConfigUpdate,
)


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

    async def update_reo_pricing_config(self, reo_id: int, data: dict) -> PricingConfigResponse:

        key = next(iter(data))
        pricing_config = await self.repository.get_by_reo_id(reo_id=reo_id)
        if not pricing_config:
            content = self._build_content_from_keys(key, data)
            create_data = PricingConfigCreate(
                is_active=True,
                reo_id=reo_id,
                content=content,
            )
            pricing_config = await self.repository.create(data=create_data.model_dump())
        else:
            content = copy.deepcopy(pricing_config.content)

            if "dynamicConfig" not in content:
                content["dynamicConfig"] = {}
            if "importantFields" not in content["dynamicConfig"]:
                content["dynamicConfig"]["importantFields"] = {}
            if "weights" not in content["dynamicConfig"]:
                content["dynamicConfig"]["weights"] = {}
            if "ranging" not in content:
                content["ranging"] = {}

            important_fields = content["dynamicConfig"]["importantFields"]
            if key not in important_fields:
                important_fields[key] = True

            if key not in content["dynamicConfig"]["weights"]:
                content["dynamicConfig"]["weights"] = self._ensure_weight(content["dynamicConfig"]["weights"], key)

            content["ranging"][key] = data[key]

            update_data = PricingConfigUpdate(is_active=True, content=content)
            pricing_config = await self.repository.update(pricing_config, update_data.model_dump())

        return PricingConfigResponse.model_validate(pricing_config)

    def _ensure_weight(self, weights: dict[str, float], key: str) -> dict[str, float]:
        if key in weights:
            return weights

        weights[key] = 0.0

        count = len(weights)

        new_weight = 1.0 / count

        for k in weights:
            weights[k] = new_weight

        return weights

    def _build_content_from_keys(self, key: str, data: dict) -> dict:
        return {
            "staticConfig": {},
            "dynamicConfig": {
                "importantFields": {key: True},
                "weights": {key: 1},
            },
            "ranging": data,
        }

    async def delete_pricing_config(self, config_id: int) -> None:
        pricing_config = await self.repository.get(config_id=config_id)
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=config_id)

        await self.repository.delete(pricing_config=pricing_config)
