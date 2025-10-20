from app.core.schemas.distribution_config_schemas import DistributionConfigResponse
from app.core.schemas.premise_schemas import PremisesResponse
from app.core.schemas.real_estate_object_schemas import RealEstateObjectFullResponse
from pydantic import BaseModel, Field


class PremisesContext(BaseModel):
    base_price: float = 0.0
    min_ref_price: float = 0.0
    max_ref_price: float = 0.0
    min_liq_rate: float = 0.0
    max_liq_rate: float = 0.0
    min_price: float = 0.0
    max_price: float = 0.0
    spread: float = 0.0

    scoring: float = 0.0
    normalized_scoring: float = 0.0
    normalized_rank: float = 0.0
    preset_value: float = 0.0
    mixed_scoring: float = 0.0
    running_total_mixed: float = 0.0
    normalized_running_total: float = 0.0
    fit_conditional_value: float = 0.0
    conditional_cost: float = 0.0
    cost_share: float = 0.0
    actual_cost: float = 0.0
    actual_price_per_sqm: float = 0.0
    final_price: float = 0.0


class PremisesWithCalculation(PremisesResponse):
    """Extended PremisesResponse with calculation fields"""

    calculation: PremisesContext = PremisesContext()


class RealEstateObjectWithCalculations(RealEstateObjectFullResponse):
    distribution_config: DistributionConfigResponse
    premises: list[PremisesWithCalculation] = Field(default_factory=list)
