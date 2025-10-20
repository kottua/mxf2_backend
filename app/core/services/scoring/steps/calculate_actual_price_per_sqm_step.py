import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateActualPricePerSQM(PipelineStep):
    """
    Calculates actual price per square meter for each premise based on
    actual cost, cost share, and premise area.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign actual price per square meter to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate actual price per square meter for")
            return context

        # Calculate actual price per square meter for each premise
        for i, premise in enumerate(context.premises):
            try:
                # Get area from premise
                area = premise.total_area_m2 or 0.0

                # Use 1e-10 to avoid division by zero if area is 0
                if area <= 0:
                    area = 1e-10
                    logger.warning(f"Premise at index {i} has zero or negative area, using 1e-10")

                # Get actual cost from previous step
                actual_cost = premise.calculation.actual_cost

                # Validate actual cost
                if actual_cost is None or math.isnan(actual_cost):
                    logger.warning(f"Invalid actual_cost for premise at index {i}, using 0")
                    actual_cost = 0.0

                # Get cost share from previous step
                cost_share = premise.calculation.cost_share

                # Validate cost share
                if cost_share is None or math.isnan(cost_share):
                    logger.warning(f"Invalid cost_share for premise at index {i}, using 0")
                    cost_share = 0.0

                # Calculate actual price per square meter
                if area == 0:
                    # This should not happen due to the 1e-10 fallback above, but just in case
                    actual_price_per_sqm = 0.0
                    logger.warning(f"Area is zero for premise at index {i}, setting actual_price_per_sqm to 0")
                else:
                    actual_price_per_sqm = (actual_cost * cost_share) / area

                # Validate result
                if math.isnan(actual_price_per_sqm) or math.isinf(actual_price_per_sqm):
                    logger.error(f"Calculated actual_price_per_sqm is NaN or Inf for premise at index {i}, using 0")
                    actual_price_per_sqm = 0.0

                # Store result in premise
                premise.calculation.actual_price_per_sqm = actual_price_per_sqm

                logger.debug(
                    f"Premise {premise.id}: area={area:.2f}, actual_cost={actual_cost:.6f}, "
                    f"cost_share={cost_share:.6f}, actual_price_per_sqm={actual_price_per_sqm:.6f}"
                )

            except Exception as e:
                logger.error(f"Error calculating actual price per square meter for premise at index {i}: {e}")
                premise.calculation.actual_price_per_sqm = 0.0

        return context
