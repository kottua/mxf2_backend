import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateActualCosts(PipelineStep):
    """
    Calculates actual costs based on total area, current price per square meter,
    and premise conditional cost shares.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign actual costs to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate actual costs for")
            return context

        # Get current price per square meter from pricing config
        current_price_per_sqm = self._get_current_price_per_sqm(context)
        if current_price_per_sqm is None:
            logger.error("Could not get current price per square meter from pricing config")
            return context

        # Calculate total area
        total_area = sum(premise.total_area_m2 or 0 for premise in context.premises)

        if total_area <= 0:
            logger.warning("Total area is zero or negative, using 1e-10")
            total_area = 1e-10

        # Calculate actual cost: total_area * current_price_per_sqm
        actual_cost = total_area * current_price_per_sqm

        # Validate actual cost
        if math.isnan(actual_cost) or math.isinf(actual_cost):
            logger.error("Calculated actual_cost is NaN or Inf, using 0")
            actual_cost = 0.0

        # Calculate actual costs for each premise
        for i, premise in enumerate(context.premises):
            try:
                # Get area from premise
                area = premise.total_area_m2 or 0.0

                # Avoid division by zero
                if area <= 0:
                    area = 1e-10
                    logger.warning(f"Premise at index {i} has zero or negative area, using 1e-10")

                # Get cost share from previous step
                cost_share = premise.calculation.cost_share

                # Validate cost share
                if cost_share is None or math.isnan(cost_share):
                    logger.warning(f"Invalid cost_share for premise at index {i}, using 0")
                    cost_share = 0.0

                # Calculate actual price per square meter
                if area == 0:
                    actual_price_per_sqm = 0.0
                else:
                    actual_price_per_sqm = (actual_cost * cost_share) / area

                # Validate result
                if math.isnan(actual_price_per_sqm) or math.isinf(actual_price_per_sqm):
                    logger.error(f"Calculated actual_price_per_sqm is NaN or Inf for premise at index {i}, using 0")
                    actual_price_per_sqm = 0.0

                # Store results in premise
                premise.calculation.actual_cost = actual_cost
                premise.calculation.actual_price_per_sqm = actual_price_per_sqm

                logger.debug(
                    f"Premise {premise.id}: area={area:.2f}, cost_share={cost_share:.6f}, "
                    f"actual_cost={actual_cost:.6f}, actual_price_per_sqm={actual_price_per_sqm:.6f}"
                )

            except Exception as e:
                logger.error(f"Error calculating actual costs for premise at index {i}: {e}")
                premise.calculation.actual_cost = 0.0
                premise.calculation.actual_price_per_sqm = 0.0

        logger.info(
            f"Calculated actual costs: total_area={total_area:.2f}, "
            f"current_price_per_sqm={current_price_per_sqm:.2f}, "
            f"actual_cost={actual_cost:.6f}"
        )

        return context

    def _get_current_price_per_sqm(self, context: RealEstateObjectWithCalculations) -> float:
        """
        Extract current price per square meter from pricing config.
        """
        try:
            if not context.pricing_configs or len(context.pricing_configs) == 0:
                logger.error("No pricing configs found")
                return 0.0

            content = context.pricing_configs[-1].content
            if not content:
                logger.error("Pricing config content is empty")
                return 0.0

            static_config = content.get("staticConfig")
            if not static_config:
                logger.error("Static config not found in pricing config")
                return 0.0

            current_price_per_sqm = static_config.get("current_price_per_sqm")
            if current_price_per_sqm is None:
                logger.error("current_price_per_sqm not found in static config")
                return 0.0

            return float(current_price_per_sqm)

        except Exception as e:
            logger.error(f"Error extracting current price per square meter: {e}")
            return 0.0
