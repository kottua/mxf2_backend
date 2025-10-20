from abc import ABC, abstractmethod

from app.core.schemas.calculation_schemas import RealEstateObjectWithCalculations


class PipelineStep(ABC):

    @abstractmethod
    def handle(self, context: RealEstateObjectWithCalculations) -> RealEstateObjectWithCalculations:
        raise NotImplementedError
