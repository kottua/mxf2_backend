import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateScope(PipelineStep):
    """
    Calculates scope (range) of normalized running total values.
    Scope is the difference between maximum and minimum values.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign scope to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate scope for")
            return context

        # Extract normalized running total values
        normalized_running_totals = []
        for i, premise in enumerate(context.premises):
            normalized_running_total = premise.calculation.normalized_running_total

            # Validate normalized running total
            if normalized_running_total is None or math.isnan(normalized_running_total):
                logger.warning(f"Invalid normalized_running_total for premise at index {i}, using 0")
                normalized_running_totals.append(0.0)
            else:
                normalized_running_totals.append(normalized_running_total)

        # Calculate scope (max - min)
        if not normalized_running_totals:
            scope = 0.0
        else:
            max_value = max(normalized_running_totals)
            min_value = min(normalized_running_totals)
            scope = max_value - min_value

        # Validate scope
        if math.isnan(scope):
            logger.error("Calculated scope is NaN, using 0")
            scope = 0.0

        # Assign scope to all premises (same value for all)
        for premise in context.premises:
            premise.calculation.fit_conditional_value = scope

        logger.debug(f"Calculated scope: {scope:.6f}")

        return context
