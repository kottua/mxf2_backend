import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import PremisesWithCalculation, RealEstateObjectWithCalculations

logger = logging.getLogger(__name__)


class CalculateSpread(PipelineStep):

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        premises_context = []
        for premise in context.premises:
            try:
                updated_premises = self.calculate_spread(premise)
                premises_context.append(updated_premises)
            except Exception as e:
                logger.error(f"Error calculating spread for premises ID {premise.id}: {e}")
                continue
        return context

    def calculate_spread(self, premises: PremisesWithCalculation) -> PremisesWithCalculation:
        max_liq_rate = premises.calculation.max_liq_rate
        min_liq_rate = premises.calculation.min_liq_rate
        if max_liq_rate is None or min_liq_rate is None or math.isnan(max_liq_rate) or math.isnan(min_liq_rate):
            logger.error("Invalid input: max_liq_rate or min_liq_rate must be valid numbers")
            premises.calculation.spread = 0.0
            return premises

        if min_liq_rate <= 0:
            logger.warning("Warning: min_liq_rate is zero or negative, using 1e-10")
            premises.calculation.spread = (max_liq_rate / 1e-10) - 1
            return premises

        premises.calculation.spread = (max_liq_rate / min_liq_rate) - 1

        return premises
