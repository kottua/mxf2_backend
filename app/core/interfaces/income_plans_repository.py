from abc import ABC, abstractmethod
from typing import Any

from app.core.schemas.income_plan_schemas import BulkIncomePlanCreate, IncomePlanResponse, IncomePlanUpdate


class IncomePlanRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: BulkIncomePlanCreate) -> IncomePlanResponse:
        """Create income plans in bulk."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, plan_id: int) -> IncomePlanResponse:
        """Retrieve an income plan by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[IncomePlanResponse]:
        """Retrieve all income plans."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, plan: Any, data: IncomePlanUpdate) -> IncomePlanResponse:
        """Update an existing income plan."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, plan: Any) -> None:
        """Delete an income plan."""
        raise NotImplementedError

    @abstractmethod
    async def create_bulk_income_plans(self, data: dict, reo_id: int) -> Any:
        """Create income plans in bulk associated with a specific REO."""
        raise NotImplementedError

    @abstractmethod
    async def deactivate_active_plans(self, reo_id: int) -> None:
        """Deactivate all active income plans."""
        raise NotImplementedError
