import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateNormalizedRunningTotal(PipelineStep):
    """
    Calculates normalized running total mixed scoring values for premises.
    Normalizes each running total by dividing it by the maximum running total value.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign normalized running total to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate normalized running total for")
            return context

        # Extract running total values
        running_totals = []
        for i, premise in enumerate(context.premises):
            running_total = premise.calculation.running_total_mixed

            # Validate running total
            if running_total is None or math.isnan(running_total):
                logger.warning(f"Invalid running_total_mixed for premise at index {i}, using 0")
                running_totals.append(0.0)
            else:
                running_totals.append(running_total)

        # Find maximum running total
        max_running_total = max(running_totals) if running_totals else 0.0

        if max_running_total == 0:
            logger.warning("Warning: max running total is zero, setting all normalized_running_total to 0")
            for premise in context.premises:
                premise.calculation.normalized_running_total = 0.0
            return context

        # Calculate and assign normalized running total
        for i, premise in enumerate(context.premises):
            try:
                running_total = running_totals[i]
                normalized_running_total = running_total / max_running_total

                # Validate result
                if math.isnan(normalized_running_total):
                    logger.error(f"Calculated normalized_running_total is NaN for premise at index {i}, using 0")
                    normalized_running_total = 0.0

                premise.calculation.normalized_running_total = normalized_running_total

                logger.debug(
                    f"Premise {premise.id}: running_total_mixed={running_total:.6f}, "
                    f"normalized_running_total={normalized_running_total:.6f}"
                )

            except Exception as e:
                logger.error(f"Error calculating normalized running total for premise at index {i}: {e}")
                premise.calculation.normalized_running_total = 0.0

        return context
