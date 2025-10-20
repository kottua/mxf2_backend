import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateFitSpreadRate(PipelineStep):
    """
    Calculates fit spread rate by dividing scope by spread.
    If spread is zero or undefined, or scope is undefined, returns a small value (1e-10).
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign fit spread rate to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate fit spread rate for")
            return context

        # Get scope from the first premise (all should have the same value)
        scope = None
        if context.premises:
            scope = context.premises[0].calculation.fit_conditional_value

        # Get spread from the first premise (all should have the same value)
        spread = None
        if context.premises:
            spread = context.premises[0].calculation.spread

        # Check if inputs are valid
        if spread is None or spread == 0 or scope is None:
            logger.warning(
                "Spread is zero or undefined, or scope is undefined/empty, " "returning a small value (1e-10)"
            )
            fit_spread_rate = 1e-10
        else:
            # Calculate fit spread rate: scope / spread
            fit_spread_rate = scope / spread

            # Validate result
            if math.isnan(fit_spread_rate) or math.isinf(fit_spread_rate):
                logger.error("Calculated fit_spread_rate is NaN or Inf, using small value (1e-10)")
                fit_spread_rate = 1e-10

        # Assign fit spread rate to all premises (same value for all)
        for premise in context.premises:
            premise.calculation.conditional_cost = fit_spread_rate

        logger.debug(
            f"Calculated fit spread rate: scope={scope}, spread={spread}, " f"fit_spread_rate={fit_spread_rate:.10f}"
        )

        return context
