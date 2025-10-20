import logging

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import RealEstateObjectWithCalculations

logger = logging.getLogger(__name__)


class CalculateNormalizedRanks(PipelineStep):

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        premises_count = len(context.premises)
        # Validate input
        if premises_count == 0:
            logger.warning("No premises to calculate normalized ranks for")
            return context

        # Calculate normalized ranks
        normalized_ranks = self._calculate_normalized_ranks(premises_count)

        if not normalized_ranks:
            logger.error("Failed to calculate normalized ranks")
            return context

        # Assign normalized ranks to premises
        for i, premise in enumerate(context.premises):
            premise.calculation.normalized_rank = normalized_ranks[i]
            logger.debug(
                f"Premise {premise.id}: scoring={premise.calculation.scoring:.4f}, "
                f"normalized_rank={normalized_ranks[i]:.6f}"
            )

        return context

    def _calculate_normalized_ranks(self, flats_count: int) -> list[float]:
        """
        Calculates normalized ranks for a given number of flats.
        Returns an array of normalized ranks (e.g., [1/n, 2/n, ..., 1] for n flats),
        or an empty array if input is invalid.
        """
        # Validate input
        if flats_count <= 0:
            logger.error("Invalid input: flats_count must be a positive integer")
            return []

        # Handle edge case: single flat
        if flats_count == 1:
            logger.warning("Warning: flats_count is 1, returning [0]")
            return [0.0]

        # Generate ranks [1, 2, ..., flats_count]
        max_rank = flats_count
        asc_scoring_ranks = list(range(1, max_rank + 1))

        # Normalize ranks
        normalized_ranks = []
        for rank in asc_scoring_ranks:
            normalized = rank / max_rank

            if normalized == 0:
                logger.warning("Warning: normalized rank is zero, using 1e-10")
                normalized_ranks.append(1e-10)
            else:
                normalized_ranks.append(normalized)

        return normalized_ranks
