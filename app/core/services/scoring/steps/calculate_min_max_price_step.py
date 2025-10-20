import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import PremisesWithCalculation, RealEstateObjectWithCalculations

logger = logging.getLogger(__name__)


class CalculateMinMaxPrice(PipelineStep):

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        premises_context = []
        for premise in context.premises:
            try:
                updated_premises = self.calculate_min_max_price(premise)
                premises_context.append(updated_premises)
            except Exception as e:
                logger.error(f"Error calculating min/max price for premises ID {premise.id}: {e}")
                continue
        return context

    def calculate_min_max_price(self, premises: PremisesWithCalculation) -> PremisesWithCalculation:
        base_price = premises.calculation.base_price
        min_liq_rate = premises.calculation.min_liq_rate
        max_liq_rate = premises.calculation.max_liq_rate
        if (
            base_price is None
            or math.isnan(base_price)
            or min_liq_rate is None
            or math.isnan(min_liq_rate)
            or max_liq_rate is None
            or math.isnan(max_liq_rate)
        ):
            logger.error("Invalid input: base_price, min_liq_rate, or max_liq_rate is undefined or not a number")
            premises.calculation.min_price = 0.0
            premises.calculation.max_price = 0.0
            return premises

        if min_liq_rate == 0:
            logger.warning("Warning: min_liq_rate is zero, using 1e-10")
            min_liq_rate = 1e-10

        if max_liq_rate == 0:
            logger.warning("Warning: max_liq_rate is zero, using 1e-10")
            max_liq_rate = 1e-10

        premises.calculation.min_price = base_price * min_liq_rate
        premises.calculation.max_price = base_price * max_liq_rate

        return premises
