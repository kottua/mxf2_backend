import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateConditionalCosts(PipelineStep):
    """
    Calculates conditional costs based on fit conditional values and premise areas.
    Returns conditional costs, total conditional cost, and premise conditional cost shares.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign conditional costs to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate conditional costs for")
            return context

        # Initialize variables
        total_cond_cost = 0.0
        conditional_costs = []

        # Calculate conditional costs for each premise
        for i, premise in enumerate(context.premises):
            try:
                # Get area from premise
                area = premise.total_area_m2 or 0.0

                # Validate area
                if area < 0:
                    logger.warning(f"Negative area for premise at index {i}, using 0")
                    area = 0.0

                # Get fit conditional value
                fit_cond_value = premise.calculation.fit_conditional_value

                # Validate fit conditional value
                if fit_cond_value is None or math.isnan(fit_cond_value):
                    logger.warning(f"Invalid fit_conditional_value for premise at index {i}, using 0")
                    fit_cond_value = 0.0

                # Calculate conditional cost: fit_cond_value * area
                cond_cost = fit_cond_value * area

                # Validate result
                if math.isnan(cond_cost) or math.isinf(cond_cost):
                    logger.error(f"Calculated cond_cost is NaN or Inf for premise at index {i}, using 0")
                    cond_cost = 0.0

                # Store conditional cost in premise
                premise.calculation.conditional_cost = cond_cost

                # Add to total
                total_cond_cost += cond_cost

                # Store in conditional costs array
                conditional_costs.append(
                    {"unit_number": premise.number_of_unit, "fit_cond_value": fit_cond_value, "cond_cost": cond_cost}
                )

                logger.debug(
                    f"Premise {premise.id}: area={area:.2f}, fit_cond_value={fit_cond_value:.6f}, "
                    f"cond_cost={cond_cost:.6f}"
                )

            except Exception as e:
                logger.error(f"Error calculating conditional cost for premise at index {i}: {e}")
                premise.calculation.conditional_cost = 0.0

        # Calculate premise conditional cost shares
        for i, premise in enumerate(context.premises):
            try:
                cond_cost = premise.calculation.conditional_cost

                if total_cond_cost == 0:
                    cost_share = 0.0
                else:
                    cost_share = cond_cost / total_cond_cost

                # Validate result
                if math.isnan(cost_share) or math.isinf(cost_share):
                    logger.error(f"Calculated cost_share is NaN or Inf for premise at index {i}, using 0")
                    cost_share = 0.0

                premise.calculation.cost_share = cost_share

                logger.debug(f"Premise {premise.id}: cond_cost={cond_cost:.6f}, " f"cost_share={cost_share:.6f}")

            except Exception as e:
                logger.error(f"Error calculating cost share for premise at index {i}: {e}")
                premise.calculation.cost_share = 0.0

        logger.info(
            f"Calculated conditional costs: total_cond_cost={total_cond_cost:.6f}, "
            f"premises_count={len(context.premises)}"
        )

        return context
