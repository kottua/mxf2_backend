import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import PremisesWithCalculation, RealEstateObjectWithCalculations

logger = logging.getLogger(__name__)


class CalculateMinMaxRate(PipelineStep):

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        premises_context = []
        for premise in context.premises:
            try:
                updated_premises = self.calculate_min_max_rate(premise)
                premises_context.append(updated_premises)
            except Exception as e:
                logger.error(f"Error calculating min/max rate for premises ID {premise.id}: {e}")
                continue
        return context

    def calculate_min_max_rate(self, premises: PremisesWithCalculation) -> PremisesWithCalculation:
        min_liq_refusal_price = premises.calculation.min_ref_price
        max_liq_refusal_price = premises.calculation.max_ref_price
        if (
            min_liq_refusal_price is None
            or math.isnan(min_liq_refusal_price)
            or max_liq_refusal_price is None
            or math.isnan(max_liq_refusal_price)
        ):
            logger.error("Invalid input: min_liq_refusal_price or max_liq_refusal_price is undefined or not a number")
            premises.calculation.min_liq_rate = 0.0
            premises.calculation.max_liq_rate = 0.0
            return premises

        if min_liq_refusal_price == 0:
            logger.warning("Warning: min_liq_refusal_price is zero, using 1e-10")
            min_liq_refusal_price = 1e-10

        if max_liq_refusal_price == 0:
            logger.warning("Warning: max_liq_refusal_price is zero, using 1e-10")
            max_liq_refusal_price = 1e-10

        premises.calculation.min_liq_rate = min_liq_refusal_price
        premises.calculation.max_liq_rate = max_liq_refusal_price

        return premises
