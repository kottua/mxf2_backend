from app.core.interfaces.distribution_configs_repository import DistributionConfigsRepositoryInterface
from app.core.interfaces.real_estate_object_repository import RealEstateObjectRepositoryInterface
from app.core.schemas.calculation_schemas import RealEstateObjectWithCalculations
from app.core.schemas.real_estate_object_schemas import RealEstateObjectFullResponse
from app.core.services.scoring import CalculateBasePrice, ScoringPipeline
from app.core.services.scoring.steps import (
    CalculateActualCosts,
    CalculateActualPricePerSQM,
    CalculateConditionalCosts,
    CalculateFinalPrice,
    CalculateFitCondValues,
    CalculateFitSpreadRate,
    CalculateMinMaxPrice,
    CalculateMinMaxRate,
    CalculateMixedScoring,
    CalculateNormalizedRanks,
    CalculateNormalizedRunningTotal,
    CalculateNormalizedScoring,
    CalculatePresetValues,
    CalculateRunningTotalMixedScoring,
    CalculateScope,
    CalculateSpread,
    FilterAndScoreFlats,
)


class ScoringCalculationService:
    def __init__(
        self,
        reo_repository: RealEstateObjectRepositoryInterface,
        distribution_config_repository: DistributionConfigsRepositoryInterface,
    ):
        self.reo_repository = reo_repository
        self.distribution_config_repository = distribution_config_repository

    async def calculate_scoring(self, reo_id: int, distribution_config_id: int) -> RealEstateObjectWithCalculations:
        reo = await self.reo_repository.get_full(id=reo_id)
        distribution_config = await self.distribution_config_repository.get(config_id=distribution_config_id)
        reo_pydantic = RealEstateObjectFullResponse.model_validate(reo)
        reo_context = RealEstateObjectWithCalculations(
            **reo_pydantic.model_dump(), distribution_config=distribution_config
        )
        steps = [
            CalculateBasePrice(),
            CalculateMinMaxRate(),
            CalculateMinMaxPrice(),
            CalculateSpread(),
            FilterAndScoreFlats(),
            CalculateNormalizedRanks(),
            CalculateNormalizedScoring(),
            CalculatePresetValues(),
            CalculateMixedScoring(),
            CalculateRunningTotalMixedScoring(),
            CalculateNormalizedRunningTotal(),
            CalculateScope(),
            CalculateFitSpreadRate(),
            CalculateFitCondValues(),
            CalculateConditionalCosts(),
            CalculateActualCosts(),
            CalculateActualPricePerSQM(),
            CalculateFinalPrice(),
        ]
        pipeline = ScoringPipeline(steps=steps)
        result = pipeline.execute(context=reo_context)

        return RealEstateObjectWithCalculations.model_validate(result)
