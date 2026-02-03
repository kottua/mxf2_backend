import copy
from datetime import datetime

from app.core.exceptions import ObjectNotFound
from app.core.interfaces.pricing_config_repository import PricingConfigRepositoryInterface
from app.core.schemas.distribution_config_schemas import DistributionConfigResponse
from app.core.schemas.income_plan_schemas import IncomePlanResponse
from app.core.schemas.premise_schemas import PremisesCreate
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

    async def get_active_pricing_config(self, reo_id: int) -> PricingConfigResponse | None:
        pricing_config = await self.repository.get_by_reo_id(reo_id=reo_id)
        if not pricing_config:
            return None
        return PricingConfigResponse.model_validate(pricing_config)

    async def get_pricing_config(self, reo_id: int) -> PricingConfigResponse:
        pricing_config = await self.repository.get_by_reo_id(reo_id=reo_id)
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=reo_id)

        return PricingConfigResponse.model_validate(pricing_config)

    async def get_all_pricing_configs(self) -> list[PricingConfigResponse]:
        pricing_configs = await self.repository.get_all()
        return [PricingConfigResponse.model_validate(config) for config in pricing_configs]

    async def update_pricing_config(self, config_id: int, data: PricingConfigUpdate) -> PricingConfigResponse:
        pricing_config = await self.repository.get(plan_id=config_id)
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=config_id)

        pricing_config = await self.repository.update(pricing_config, data.model_dump())
        return PricingConfigResponse.model_validate(pricing_config)

    async def update_reo_pricing_config(self, reo_id: int, data: dict) -> PricingConfigResponse:
        is_weighted_factors = "dynamicConfig" in data and isinstance(data.get("dynamicConfig"), dict)

        if is_weighted_factors:
            return await self._update_reo_pricing_config_weighted_factors(reo_id=reo_id, data=data)
        return await self._update_reo_pricing_config_ranging(reo_id=reo_id, data=data)

    async def _update_reo_pricing_config_weighted_factors(self, reo_id: int, data: dict) -> PricingConfigResponse:
        """Обновляет только dynamicConfig.importantFields и dynamicConfig.weights (результат агента weighted factors)."""
        dconf = data["dynamicConfig"]
        new_important_fields = dict(dconf.get("importantFields", {}))
        new_weights = dict(dconf.get("weights", {}))

        pricing_config = await self.repository.get_by_reo_id(reo_id=reo_id)
        if not pricing_config:
            content = {
                "staticConfig": {},
                "dynamicConfig": {
                    "importantFields": new_important_fields,
                    "weights": new_weights,
                },
                "ranging": {},
            }
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
            content["dynamicConfig"]["importantFields"] = new_important_fields
            content["dynamicConfig"]["weights"] = new_weights
            if "ranging" not in content:
                content["ranging"] = {}

            update_data = PricingConfigUpdate(is_active=True, content=content)
            pricing_config = await self.repository.update(pricing_config, update_data.model_dump())

        return PricingConfigResponse.model_validate(pricing_config)

    async def _update_reo_pricing_config_ranging(self, reo_id: int, data: dict) -> PricingConfigResponse:
        """Обновляет ranging и при необходимости importantFields/weights для одного поля (результат ranging-агентов)."""
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
            if key not in important_fields or not important_fields[key]:
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

    async def delete_pricing_config(self, plan_id: int) -> None:
        pricing_config = await self.repository.get(plan_id=plan_id)
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=plan_id)

        await self.repository.delete(pricing_config=pricing_config)

    def calculate_current_price_per_sqm(
        self,
        all_premises: list[PremisesCreate],
        available_premises: list[PremisesCreate],
        active_plans: list[IncomePlanResponse],
    ) -> float:
        """
        Вычисляет current_price_per_sqm.

        Логика:
        - Если есть active_plans: интерполяция на основе soldout (доли проданных помещений)
        - Если нет active_plans: средняя цена из available помещений

        Args:
            all_premises: Все помещения (для расчета soldout)
            available_premises: Доступные помещения с ценами (для базовой цены)
            active_plans: Активные планы доходов (опционально)

        Returns:
            float: Рассчитанная цена за м², округленная до 2 знаков
        """
        prices = [p.price_per_meter for p in available_premises if p.price_per_meter]
        base_price = sum(prices) / len(prices) if prices else 0.0

        sold_count = sum(1 for p in all_premises if p.status == "sold")
        total_count = len(all_premises)
        soldout = sold_count / total_count if total_count > 0 else 0.0

        try:
            sorted_plans = sorted(
                active_plans,
                key=lambda x: (
                    datetime.fromisoformat(x.period_begin.replace("Z", "+00:00"))
                    if isinstance(x.period_begin, str)
                    else (x.period_begin if hasattr(x.period_begin, "isoformat") else datetime.min)
                ),
            )
        except (ValueError, AttributeError):
            sorted_plans = active_plans

        plan_count = len(sorted_plans)
        calculated_price = base_price

        for i, plan in enumerate(sorted_plans):
            start = i / plan_count
            end = (i + 1) / plan_count

            if start <= soldout <= end:
                price_start = plan.price_per_sqm
                next_plan = sorted_plans[i + 1] if i + 1 < plan_count else None
                price_end = next_plan.price_per_sqm if next_plan else price_start

                if end != start:
                    progress = (soldout - start) / (end - start)
                else:
                    progress = 0

                calculated_price = price_start + (price_end - price_start) * progress
                break

        if calculated_price == base_price and sorted_plans:
            calculated_price = sorted_plans[0].price_per_sqm

        return round(calculated_price, 2)

    async def sync_pricing_config_after_premises_upload(
        self,
        reo_id: int,
        premises: list[PremisesCreate],
        active_plans: list[IncomePlanResponse],
        distribution_config: DistributionConfigResponse,
    ) -> PricingConfigResponse:
        available_premises = [
            p for p in premises if p.status == "available" and p.price_per_meter is not None and p.price_per_meter > 0
        ]
        calculated_current_price = self.calculate_current_price_per_sqm(
            all_premises=premises,
            available_premises=available_premises,
            active_plans=active_plans,
        )

        # Проверяем существование pricing config
        pricing_config = await self.get_active_pricing_config(reo_id=reo_id)

        if not pricing_config:
            # Создаем новый pricing config
            oversold_method = "pieces"

            # Вычисляем min/max цены из available_premises
            prices = [p.price_per_meter for p in available_premises if p.price_per_meter]
            minimum_liq_refusal_price = round(min(prices, default=0), 2)
            maximum_liq_refusal_price = round(max(prices, default=0), 2)

            config = PricingConfigCreate(
                is_active=True,
                reo_id=reo_id,
                content={
                    "staticConfig": {
                        "bargainGap": 0,
                        "maxify_factor": 0,
                        "current_price_per_sqm": round(calculated_current_price, 2),  # Змінюється кожного разу
                        "onboarding_current_price_per_sqm": round(
                            calculated_current_price, 2
                        ),  # НЕ змінюється кожного разу
                        "minimum_liq_refusal_price": minimum_liq_refusal_price,  # НЕ змінюється кожного разу
                        "maximum_liq_refusal_price": maximum_liq_refusal_price,  # НЕ змінюється кожного разу
                        "overestimate_correct_factor": 0.01,
                        "oversold_method": oversold_method,
                        "sigma": 0.1,
                        "similarityThreshold": 0.01,
                        "distribConfigId": distribution_config.id,
                    },
                    "dynamicConfig": {
                        "importantFields": {},
                        "weights": {},
                    },
                    "ranging": {},
                },
            )

            return await self.create_pricing_config(data=config)
        else:
            # Обновляем существующий pricing config
            existing_content = pricing_config.content or {}
            static_config = existing_content.get("staticConfig", {})
            static_config["current_price_per_sqm"] = round(calculated_current_price, 2)
            existing_content["staticConfig"] = static_config

            upd_config = PricingConfigUpdate(content=existing_content)

            return await self.update_pricing_config(
                config_id=pricing_config.id,
                data=upd_config,
            )
