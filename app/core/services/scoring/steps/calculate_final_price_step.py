import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateFinalPrice(PipelineStep):
    """
    Calculates final price for each premise based on base price, fit conditional values,
    static config parameters, and min/max price constraints.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign final price to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate final price for")
            return context

        # Get base price from the first premise (all should have the same base price)
        base_price = None
        if context.premises:
            base_price = context.premises[0].calculation.base_price

        if base_price is None or math.isnan(base_price):
            logger.error("Invalid base price, using 0")
            base_price = 0.0

        # Get min and max prices from premises
        min_price = None
        max_price = None
        for premise in context.premises:
            if min_price is None or premise.calculation.min_price < min_price:
                min_price = premise.calculation.min_price
            if max_price is None or premise.calculation.max_price > max_price:
                max_price = premise.calculation.max_price

        # Validate min/max prices
        if min_price is None or math.isnan(min_price):
            logger.warning("Invalid min_price, using 0")
            min_price = 0.0
        if max_price is None or math.isnan(max_price):
            logger.warning("Invalid max_price, using infinity")
            max_price = float("inf")

        # Get static config parameters
        bargain_gap = self._get_bargain_gap(context)
        if bargain_gap is None:
            logger.warning("Could not get bargain_gap from static config, using 0")
            bargain_gap = 0.0

        # Calculate final price for each premise
        for i, premise in enumerate(context.premises):
            try:
                # Get fit conditional value
                fit_cond_value = premise.calculation.fit_conditional_value

                # Validate fit conditional value
                if fit_cond_value is None or math.isnan(fit_cond_value):
                    logger.warning(f"Invalid fit_conditional_value for premise at index {i}, using 1")
                    fit_cond_value = 1.0

                # Calculate price: basePrice * fitCondValue * (1 - bargainGap/100)
                price = base_price * fit_cond_value * (1 - bargain_gap / 100)

                # Clamp price between minPrice and maxPrice
                price = max(price, min_price)
                if max_price != float("inf"):
                    price = min(price, max_price)

                # Validate result
                if math.isnan(price) or math.isinf(price):
                    logger.error(f"Calculated final_price is NaN or Inf for premise at index {i}, using min_price")
                    price = min_price

                premise.calculation.final_price = price

                logger.debug(
                    f"Premise {premise.id}: base_price={base_price:.6f}, "
                    f"fit_cond_value={fit_cond_value:.6f}, bargain_gap={bargain_gap:.2f}, "
                    f"final_price={price:.6f}"
                )

            except Exception as e:
                logger.error(f"Error calculating final price for premise at index {i}: {e}")
                premise.calculation.final_price = min_price

        max_price_str = f"{max_price:.6f}" if max_price != float("inf") else "inf"
        logger.info(
            f"Calculated final prices: base_price={base_price:.6f}, "
            f"bargain_gap={bargain_gap:.2f}, min_price={min_price:.6f}, "
            f"max_price={max_price_str}"
        )

        return context

    def _get_bargain_gap(self, context: RealEstateObjectWithCalculations) -> float:
        """
        Extract bargain gap from static config.
        """
        try:
            if not context.pricing_config:
                logger.error("No pricing config found")
                return 0.0

            content = context.pricing_config.content
            if not content:
                logger.error("Pricing config content is empty")
                return 0.0

            static_config = content.get("staticConfig")
            if not static_config:
                logger.error("Static config not found in pricing config")
                return 0.0

            bargain_gap = static_config.get("bargainGap")
            if bargain_gap is None:
                logger.error("bargainGap not found in static config")
                return 0.0

            return float(bargain_gap)

        except Exception as e:
            logger.error(f"Error extracting bargain gap: {e}")
            return 0.0
