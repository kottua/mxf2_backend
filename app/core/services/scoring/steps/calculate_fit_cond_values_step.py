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
        static_config = self._get_onboarding_current_price_per_sqm(context)
        onboarding_current_price_per_sqm = static_config.get("onboarding_current_price_per_sqm", 0.0)
        minimum_liq_refusal_price = static_config.get("minimum_liq_refusal_price", 0.0)
        maximum_liq_refusal_price = static_config.get("maximum_liq_refusal_price", 0.0)

        # Calculate b_rate_net and t_rate_net
        b_rate_net = 1 - minimum_liq_refusal_price / onboarding_current_price_per_sqm
        t_rate_net = maximum_liq_refusal_price / onboarding_current_price_per_sqm - 1

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

    def _get_onboarding_current_price_per_sqm(self, context: RealEstateObjectWithCalculations) -> dict:
        """
        Extract onboarding current price per square meter from pricing config.
        """
        initial_price_data = {
            "onboarding_current_price_per_sqm": 0.0,
            "minimum_liq_refusal_price": 0.0,
            "maximum_liq_refusal_price": 0.0,
        }

        try:
            if not context.pricing_configs or len(context.pricing_configs) == 0:
                logger.error("No pricing configs found")
                return initial_price_data

            content = context.pricing_configs[-1].content

            static_config = content.get("staticConfig", {})

            onboarding_current_price_per_sqm = static_config.get("onboarding_current_price_per_sqm", None)
            if onboarding_current_price_per_sqm is None:
                logger.error("onboarding_current_price_per_sqm not found in static config")
                initial_price_data["onboarding_current_price_per_sqm"] = 0.0

            maximum_liq_refusal_price = static_config.get("maximum_liq_refusal_price", None)
            if maximum_liq_refusal_price is None:
                logger.error("maximum_liq_refusal_price not found in static config")
                initial_price_data["maximum_liq_refusal_price"] = 0.0

            minimum_liq_refusal_price = static_config.get("minimum_liq_refusal_price", None)
            if minimum_liq_refusal_price is None:
                logger.error("minimum_liq_refusal_price not found in static config")
                initial_price_data["minimum_liq_refusal_price"] = 0.0

            return {
                "onboarding_current_price_per_sqm": float(onboarding_current_price_per_sqm),
                "minimum_liq_refusal_price": float(minimum_liq_refusal_price),
                "maximum_liq_refusal_price": float(maximum_liq_refusal_price),
            }

        except Exception as e:
            logger.error(f"Error extracting current price per square meter: {e}")
            return initial_price_data
