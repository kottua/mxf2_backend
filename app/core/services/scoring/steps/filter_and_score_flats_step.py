import logging
import math
from typing import List, TypedDict

from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import PremisesWithCalculation, RealEstateObjectWithCalculations
from app.core.schemas.pricing_config_schemas import PricingConfigResponse

logger = logging.getLogger(__name__)


class FilterAndScoreFlats(PipelineStep):

    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        updated_premises = []

        # Get available premises only
        available_premises = [p for p in context.premises if p.status == "available"]

        if not available_premises:
            logger.warning("No available premises found")
            context.premises = []
            return context

        # Check if pricing config is valid
        if not context.pricing_configs or not context.pricing_configs[-1].content:
            logger.error("Invalid pricing config")
            return context

        config = context.pricing_configs[-1]
        if (
            not config.content.get("dynamicConfig")
            or not config.content.get("staticConfig")
            or not config.content.get("ranging")
        ):
            logger.error("Incomplete pricing config")
            return context

        # Process each available premise
        for premise in available_premises:
            try:
                updated_premise = self.calculate_scoring(premise, context.premises, config)
                updated_premises.append(updated_premise)
            except Exception as e:
                logger.error(f"Error calculating scoring for premise ID {premise.id}: {e}")
                continue

        # Sort by scoring in ascending order
        updated_premises.sort(key=lambda p: p.calculation.scoring)

        context.premises = updated_premises
        return context

    def calculate_scoring(
        self,
        premise: PremisesWithCalculation,
        all_premises: list[PremisesWithCalculation],
        config: PricingConfigResponse,
    ) -> PremisesWithCalculation:
        """Calculate scoring for a single premise"""

        # Get selected fields
        selected_fields = [
            field
            for field, is_selected in config.content.get("dynamicConfig", {}).get("importantFields", {}).items()
            if is_selected
        ]

        if not selected_fields:
            logger.warning("No selected important fields, setting scoring to 0")
            premise.calculation.scoring = 0.0
            return premise

        # Build scoring fields configuration
        scoring_fields = []
        weights = []

        for field in selected_fields:
            content = config.content or {}
            dynamic_config = content.get("dynamicConfig") or {}
            ranging = content.get("ranging") or {}

            weight = (dynamic_config.get("weights") or {}).get(field, 0)
            priorities = ranging.get(field, [])

            scoring_fields.append(
                {
                    "field": field,
                    "weight": float(weight),
                    "priorities": priorities,
                }
            )
            weights.append(float(weight))

        # Calculate max ranks for each field
        max_ranks = []
        for field_config in scoring_fields:
            priorities = field_config.get("priorities", [])
            if priorities:
                max_rank = max(p.get("priority", 1) for p in priorities)
            else:
                max_rank = 1
            max_ranks.append(max_rank)

        # Get ranks for target premise
        target_ranks: List[int] = [self._get_rank_for_field(premise, field_config) for field_config in scoring_fields]

        # Get sold flats
        class SoldFlatDict(TypedDict):
            flat: PremisesWithCalculation
            features: List[int]

        sold_flats: List[SoldFlatDict] = [
            {
                "flat": flat,
                "features": [self._get_rank_for_field(flat, field_config) for field_config in scoring_fields],
            }
            for flat in all_premises
            if flat.status == "sold"
        ]

        # Calculate scoring
        if not sold_flats:
            # No sold flats - use inverse ranks
            inverse_ranks = [max_ranks[i] - rank + 1 for i, rank in enumerate(target_ranks)]

            # Normalize inverse ranks
            normalized_inverse_ranks = [
                inverse_rank / max_ranks[i] if max_ranks[i] > 0 else 0 for i, inverse_rank in enumerate(inverse_ranks)
            ]

            # Calculate raw score
            raw_score = sum(norm_rank * weights[i] for i, norm_rank in enumerate(normalized_inverse_ranks))

            premise.calculation.scoring = round(raw_score, 4)
        else:
            # With sold flats - use similarity-based scoring
            sigma_raw = ((config.content or {}).get("staticConfig") or {}).get("sigma")
            similarity_threshold_raw = ((config.content or {}).get("staticConfig") or {}).get("similarityThreshold")

            # Ensure numeric values with sensible defaults
            sigma: float = float(sigma_raw) if sigma_raw is not None else 1.0
            if sigma <= 0:
                sigma = 1e-9
            similarity_threshold: float = (
                float(similarity_threshold_raw) if similarity_threshold_raw is not None else 0.0
            )

            # Calculate factor similarities
            factor_similarities = [0.0] * len(scoring_fields)

            for sold_flat in sold_flats:
                for i in range(len(scoring_fields)):
                    diff = abs(target_ranks[i] - sold_flat["features"][i])
                    normalized_diff = diff / max_ranks[i] if max_ranks[i] > 0 else 0

                    # Gaussian similarity
                    similarity = math.exp(-(normalized_diff**2) / (2 * sigma**2))

                    if similarity > similarity_threshold:
                        factor_similarities[i] += similarity

            # Normalize similarities
            max_similarity = max(factor_similarities) if factor_similarities else 1
            normalized_similarities = [s / max_similarity if max_similarity > 0 else 0 for s in factor_similarities]

            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight if total_weight > 0 else 0 for w in weights]

            # Calculate final score
            final_score = sum(sim * normalized_weights[i] for i, sim in enumerate(normalized_similarities))

            premise.calculation.scoring = round(final_score, 6)

        return premise

    def _get_rank_for_field(self, flat: PremisesWithCalculation, field_config: dict) -> int:
        """Get rank for a specific field based on priorities"""
        field_name = field_config["field"]
        priorities = field_config.get("priorities", [])

        # Get value from flat
        value = getattr(flat, field_name, None)

        if value is None:
            # Return max priority if value is missing
            if priorities:
                return max(p.get("priority", 1) for p in priorities)
            return 1

        # Try numeric comparison first
        try:
            numeric_value = float(value)
            for priority_group in priorities:
                values = priority_group.get("values", [])
                if str(numeric_value) in values or numeric_value in values:
                    return priority_group.get("priority", 1)
        except (ValueError, TypeError):
            pass

        # String comparison
        string_value = str(value)
        for priority_group in priorities:
            values = priority_group.get("values", [])
            if string_value in values:
                return priority_group.get("priority", 1)

        # Return max priority if no match found
        if priorities:
            return max(p.get("priority", 1) for p in priorities)
        return 1
