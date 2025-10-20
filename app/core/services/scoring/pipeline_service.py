from app.core.interfaces.base_step import PipelineStep
from app.core.schemas.calculation_schemas import RealEstateObjectWithCalculations


class ScoringPipeline:
    def __init__(self, steps: list[PipelineStep]):
        self.steps = steps

    def execute(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        for step in self.steps:
            try:
                context = step.handle(context=context)
            except Exception as e:
                step_name = step.__class__.__name__
                print(f"Error in step {step_name}: {e}")
                continue

        return context
