import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateMixedScoring(PipelineStep):
    """
    Calculates mixed scoring values for premises.
    Combines normalized scoring with preset values using the formula:
    mixed_scoring = normalized_scoring + (normalized_scoring * preset_value)
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign mixed scoring to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate mixed scoring for")
            return context

        # Calculate mixed scoring for each premise
        for i, premise in enumerate(context.premises):
            try:
                # Get normalized scoring and preset value
                normalized_scoring = premise.calculation.normalized_scoring
                preset_value = premise.calculation.preset_value

                # Validate inputs
                if normalized_scoring is None or math.isnan(normalized_scoring):
                    logger.warning(f"Invalid normalized_scoring for premise at index {i}, using 0")
                    normalized_scoring = 0.0

                if preset_value is None or math.isnan(preset_value):
                    logger.warning(f"Invalid preset_value for premise at index {i}, using 0")
                    preset_value = 0.0

                # Calculate mixed scoring: score + score * preset_value
                mixed_scoring = normalized_scoring + (normalized_scoring * preset_value)

                # Validate result
                if math.isnan(mixed_scoring):
                    logger.error(f"Calculated mixed_scoring is NaN for premise at index {i}, using 0")
                    mixed_scoring = 0.0

                premise.calculation.mixed_scoring = mixed_scoring

                logger.debug(
                    f"Premise {premise.id}: normalized_scoring={normalized_scoring:.6f}, "
                    f"preset_value={preset_value:.6f}, mixed_scoring={mixed_scoring:.6f}"
                )

            except Exception as e:
                logger.error(f"Error calculating mixed scoring for premise at index {i}: {e}")
                premise.calculation.mixed_scoring = 0.0

        return context
