from abc import ABC, abstractmethod
from typing import Any

from app.core.schemas.pricing_config_schemas import PricingConfigCreate


class PricingConfigRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: PricingConfigCreate) -> Any:
        """Create pricing config in bulk."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, config_id: int) -> Any:
        """Retrieve an pricing config by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_reo_id(self, reo_id: int) -> Any:
        """Retrieve an active pricing config by its REO ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Any]:
        """Retrieve all pricing config."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, pricing_config: Any, data: dict) -> Any:
        """Update an existing pricing config."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, pricing_config: Any) -> None:
        """Delete an pricing_config."""
        raise NotImplementedError

    @abstractmethod
    async def deactivate_active_pricing_configs(self, reo_id: int) -> None:
        """Deactivate all active income plans."""
        raise NotImplementedError
