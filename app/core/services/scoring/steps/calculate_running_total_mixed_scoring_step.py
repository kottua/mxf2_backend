import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateRunningTotalMixedScoring(PipelineStep):
    """
    Calculates running total mixed scoring values for premises.
    Creates a cumulative sum of mixed scoring values where each element
    is the sum of all previous mixed scoring values plus the current one.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign running total mixed scoring to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate running total mixed scoring for")
            return context

        # Initialize running total
        running_total = 0.0

        # Calculate running total for each premise
        for i, premise in enumerate(context.premises):
            try:
                # Get mixed scoring value
                mixed_scoring = premise.calculation.mixed_scoring

                # Validate mixed scoring
                if mixed_scoring is None or math.isnan(mixed_scoring):
                    logger.warning(f"Invalid mixed_scoring for premise at index {i}, using 0")
                    mixed_scoring = 0.0

                # For the first premise, running total is 0
                # For subsequent premises, add current mixed scoring to previous running total
                if i == 0:
                    running_total = 0.0
                else:
                    running_total += mixed_scoring

                premise.calculation.running_total_mixed = running_total

                logger.debug(
                    f"Premise {premise.id}: mixed_scoring={mixed_scoring:.6f}, "
                    f"running_total_mixed={running_total:.6f}"
                )

            except Exception as e:
                logger.error(f"Error calculating running total mixed scoring for premise at index {i}: {e}")
                premise.calculation.running_total_mixed = 0.0

        return context
