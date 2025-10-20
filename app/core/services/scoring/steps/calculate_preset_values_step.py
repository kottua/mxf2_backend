import logging
import math

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import (
    RealEstateObjectWithCalculations,
)
from app.core.schemas.distribution_config_schemas import DistributionConfigResponse

logger = logging.getLogger(__name__)


class CalculatePresetValues(PipelineStep):
    """
    Calculates preset values based on distribution configuration and normalized ranks.
    Applies distribution function (Uniform, Gaussian, or Bimodal) and maps to premises.
    """

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        """
        Calculate and assign preset values to all premises based on distribution config.
        """
        # Validate input
        if not context.premises or len(context.premises) == 0:
            logger.error("No premises to calculate preset values for")
            return context

        if not context.distribution_config:
            logger.error("No distribution config found")
            return context

        max_rank = len(context.premises)

        # Collect normalized ranks
        rank_norm = [premise.calculation.normalized_rank for premise in context.premises]

        # Apply distribution to get raw preset values
        raw_preset_values = self._apply_distribution(max_rank, context.distribution_config)

        if not raw_preset_values:
            logger.error("Failed to calculate raw preset values")
            return context

        # Map preset values to premises based on normalized ranks
        for i, premise in enumerate(context.premises):
            rank = rank_norm[i]

            # Calculate index based on normalized rank
            # Formula: floor((rank - (1 / maxRank)) * (maxRank - 1))
            index = math.floor((rank - (1 / max_rank)) * (max_rank - 1))

            # Get preset value, use last value if index out of bounds
            if 0 <= index < len(raw_preset_values):
                preset_value = raw_preset_values[index]
            else:
                preset_value = raw_preset_values[-1]

            premise.calculation.preset_value = preset_value

            logger.debug(
                f"Premise {premise.id}: normalized_rank={rank:.6f}, " f"index={index}, preset_value={preset_value:.6f}"
            )

        return context

    def _apply_distribution(self, length: int, distribution_config: DistributionConfigResponse) -> list[float]:
        """
        Applies distribution function to generate preset values.
        Supports Uniform, Gaussian, and Bimodal distributions.
        """
        if not distribution_config.content:
            logger.error("Distribution config content is empty")
            return []

        # Get function type
        function_type = distribution_config.content.get("function_type")

        if function_type is None or not isinstance(function_type, str):
            logger.warning("Warning: function_type is undefined or not a string, " "defaulting to 'Uniform'")
            function_type = "Uniform"

        params = distribution_config.content

        # Validate and apply distribution based on type
        if function_type == "Bimodal":
            return self._apply_bimodal_distribution(length, params)
        elif function_type == "Gaussian":
            return self._apply_gaussian_distribution(length, params)
        elif function_type == "Uniform":
            return self._apply_uniform_distribution(length)
        else:
            logger.warning(f"Unknown distribution type: {function_type}, returning uniform")
            return [1.0] * length

    def _apply_uniform_distribution(self, length: int) -> list[float]:
        """Uniform distribution: [1/n, 2/n, ..., n/n]"""
        return [(i + 1) / length for i in range(length)]

    def _apply_gaussian_distribution(self, length: int, params: dict) -> list[float]:
        """Gaussian distribution with mean and standard deviation"""
        mean = params.get("mean")
        std_dev = params.get("stdDev")

        # Validate mean
        if mean is None or not isinstance(mean, (int, float)) or math.isnan(mean):
            logger.warning("Warning: mean is undefined or NaN, defaulting to 0.5")
            mean = 0.5

        # Validate stdDev
        if std_dev is None or not isinstance(std_dev, (int, float)) or math.isnan(std_dev) or std_dev <= 0:
            logger.warning("Warning: stdDev is undefined, NaN, or non-positive, " "defaulting to 1/6")
            std_dev = 1 / 6

        result = []
        for i in range(length):
            x = (i + 1) / length
            z = (x - mean) / std_dev
            value = math.exp(-0.5 * z * z)
            result.append(value)

        return result

    def _apply_bimodal_distribution(self, length: int, params: dict) -> list[float]:
        """Bimodal distribution with two peaks"""
        mean1 = params.get("mean1")
        mean2 = params.get("mean2")
        std_dev = params.get("stdDev")

        # Validate and set defaults
        if mean1 is None or not isinstance(mean1, (int, float)):
            logger.warning("Warning: mean1 is not a number, defaulting to 1/3")
            mean1 = 1 / 3

        if mean2 is None or not isinstance(mean2, (int, float)):
            logger.warning("Warning: mean2 is not a number, defaulting to 2/3")
            mean2 = 2 / 3

        if std_dev is None or not isinstance(std_dev, (int, float)):
            logger.warning("Warning: stdDev is not a number, defaulting to 1/10")
            std_dev = 1 / 10

        result = []
        for i in range(length):
            x = (i + 1) / length
            z1 = (x - mean1) / std_dev
            z2 = (x - mean2) / std_dev
            value = math.exp(-0.5 * z1 * z1) + math.exp(-0.5 * z2 * z2)
            result.append(value)

        return result
