import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)

logger = logging.getLogger(__name__)


class CalculateFitCondValues(PipelineStep):
    """
    Calculates fit conditional values based on normalized running total,
    min/max liquidation rates, and current price per square meter.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign fit conditional values to all premises.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate fit conditional values for")
            return context

        # Get current price per square meter from pricing config
        current_price_per_sqm = self._get_current_price_per_sqm(context)
        if current_price_per_sqm is None:
            logger.error("Could not get current price per square meter from pricing config")
            return context

        # Get min and max liquidation rates from premises
        min_liq_rate = None
        max_liq_rate = None
        for premise in context.premises:
            if min_liq_rate is None or premise.calculation.min_liq_rate < min_liq_rate:
                min_liq_rate = premise.calculation.min_liq_rate
            if max_liq_rate is None or premise.calculation.max_liq_rate > max_liq_rate:
                max_liq_rate = premise.calculation.max_liq_rate

        # Validate inputs
        if (
            min_liq_rate is None
            or math.isnan(min_liq_rate)
            or max_liq_rate is None
            or math.isnan(max_liq_rate)
            or current_price_per_sqm is None
            or math.isnan(current_price_per_sqm)
        ):
            logger.error("Invalid liquidation rates or current price per square meter")
            return context

        if current_price_per_sqm == 0:
            logger.warning("Warning: currentPricePerSQM is zero, using 1e-10")
            current_price_per_sqm = 1e-10

        # Calculate b_rate_net and t_rate_net
        b_rate_net = 1 - min_liq_rate / current_price_per_sqm
        t_rate_net = max_liq_rate / current_price_per_sqm - 1

        # Get normalized running total values
        sp_mixed_rt_norm = [premise.calculation.normalized_running_total for premise in context.premises]

        # Find median of spMixedRtNorm
        sorted_sp_mixed_rt_norm = sorted(sp_mixed_rt_norm)
        mid = len(sorted_sp_mixed_rt_norm) // 2
        if len(sorted_sp_mixed_rt_norm) % 2 == 0:
            sp_mixed_rt_norm_med = (sorted_sp_mixed_rt_norm[mid - 1] + sorted_sp_mixed_rt_norm[mid]) / 2
        else:
            sp_mixed_rt_norm_med = sorted_sp_mixed_rt_norm[mid]

        # Calculate spMixedRtNorm_scope
        sp_mixed_rt_norm_scope = []
        for value in sp_mixed_rt_norm:
            if value <= sp_mixed_rt_norm_med:
                scope_value = sp_mixed_rt_norm_med - value
            else:
                scope_value = value - sp_mixed_rt_norm_med
            sp_mixed_rt_norm_scope.append(scope_value)

        # Get first and last scope values
        sp_mixed_rt_norm_scope_b = sp_mixed_rt_norm_scope[0]
        sp_mixed_rt_norm_scope_t = sp_mixed_rt_norm_scope[-1]

        # Check for zero to avoid division by zero
        if sp_mixed_rt_norm_scope_b == 0:
            logger.warning("Warning: spMixedRtNorm_scope_b is zero, using 1e-10")
            sp_mixed_rt_norm_scope_b = 1e-10
        if sp_mixed_rt_norm_scope_t == 0:
            logger.warning("Warning: spMixedRtNorm_scope_t is zero, using 1e-10")
            sp_mixed_rt_norm_scope_t = 1e-10

        # Calculate b_fit_transform and t_fit_transform
        b_fit_transform = sp_mixed_rt_norm_scope_b / b_rate_net
        t_fit_transform = sp_mixed_rt_norm_scope_t / t_rate_net

        # Calculate fit conditional values for each premise
        for i, premise in enumerate(context.premises):
            try:
                value = sp_mixed_rt_norm[i]
                scope_value = sp_mixed_rt_norm_scope[i]

                if value <= sp_mixed_rt_norm_med:
                    fit_cond_value = 1 - scope_value / b_fit_transform
                else:
                    fit_cond_value = 1 + scope_value / t_fit_transform

                # Validate result
                if math.isnan(fit_cond_value) or math.isinf(fit_cond_value):
                    logger.error(f"Calculated fit_cond_value is NaN or Inf for premise at index {i}, using 1e-10")
                    fit_cond_value = 1e-10

                premise.calculation.fit_conditional_value = fit_cond_value

                logger.debug(
                    f"Premise {premise.id}: value={value:.6f}, scope_value={scope_value:.6f}, "
                    f"fit_cond_value={fit_cond_value:.6f}"
                )

            except Exception as e:
                logger.error(f"Error calculating fit conditional value for premise at index {i}: {e}")
                premise.calculation.fit_conditional_value = 1e-10

        return context

    def _get_current_price_per_sqm(self, context: RealEstateObjectWithCalculations) -> float | None:
        """
        Extract current price per square meter from pricing config.
        """
        try:
            if not context.pricing_configs or len(context.pricing_configs) == 0:
                logger.error("No pricing configs found")
                return None

            content = context.pricing_configs[-1].content
            if not content:
                logger.error("Pricing config content is empty")
                return None

            static_config = content.get("staticConfig")
            if not static_config:
                logger.error("Static config not found in pricing config")
                return None

            current_price_per_sqm = static_config.get("current_price_per_sqm")
            if current_price_per_sqm is None:
                logger.error("current_price_per_sqm not found in static config")
                return None

            return float(current_price_per_sqm)

        except Exception as e:
            logger.error(f"Error extracting current price per square meter: {e}")
            return None
