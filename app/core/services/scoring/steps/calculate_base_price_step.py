import logging

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import RealEstateObjectWithCalculations

logger = logging.getLogger(__name__)


class CalculateBasePrice(PipelineStep):

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        if not context.pricing_config:
            logger.error("No pricing config found")
            return context

        static_config = context.pricing_config.content.get("staticConfig", {})
        price_per_sqm = static_config.get("current_price_per_sqm")

        if price_per_sqm is None or not isinstance(price_per_sqm, (int, float)):
            logger.error("Invalid input: price_per_sqm is undefined or not a number")
            return context

        if price_per_sqm == 0:
            logger.warning("Warning: price_per_sqm is zero, using 1e-10")
            price_per_sqm = 1e-10

        for premise in context.premises:
            premise.calculation.base_price = float(price_per_sqm)
        return context
