import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import RealEstateObjectWithCalculations

logger = logging.getLogger(__name__)


class CalculateNormalizedScoring(PipelineStep):
    """
    Calculates normalized scoring values for premises.
    Normalizes each scoring by dividing it by the maximum scoring value.
    Assigns normalized_scoring to each premise's calculation context.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign normalized scoring to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate normalized scoring for")
            return context

        # Extract scoring values
        scorings = []
        for i, premise in enumerate(context.premises):
            scoring = premise.calculation.scoring

            # Validate scoring
            if scoring is None or math.isnan(scoring):
                logger.error(f"Invalid scoring for premise at index {i}: " f"scoring is not a valid number, using 0")
                scorings.append(0.0)
            elif scoring == 0:
                logger.warning(f"Warning: scoring for premise at index {i} is zero, keeping 0")
                scorings.append(0.0)
            else:
                scorings.append(scoring)

        # Find maximum scoring
        max_scoring = max(scorings) if scorings else 0.0

        if max_scoring == 0:
            logger.warning("Warning: maxScoring is zero, setting all normalized_scoring to 0")
            for premise in context.premises:
                premise.calculation.normalized_scoring = 0.0
            return context

        # Calculate and assign normalized scoring
        for i, premise in enumerate(context.premises):
            scoring = scorings[i]
            normalized = scoring / max_scoring

            # Validate normalized value
            if math.isnan(normalized):
                logger.error(f"Invalid normalized scoring for premise at index {i}: " f"result is NaN, using 1e-10")
                normalized = 1e-10
            elif normalized == 0 and scoring != 0:
                logger.warning(f"Warning: normalized scoring for premise at index {i} is zero, " f"using 1e-10")
                normalized = 1e-10

            premise.calculation.normalized_scoring = normalized

            logger.debug(f"Premise {premise.id}: scoring={scoring:.6f}, " f"normalized_scoring={normalized:.6f}")

        return context
