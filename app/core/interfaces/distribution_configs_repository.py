from abc import ABC, abstractmethod
from typing import Any


class DistributionConfigsRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> dict:
        """Create a new distribution configuration."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, config_id: int) -> dict | None:
        """Retrieve a distribution configuration by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, config: Any, data: dict) -> dict | None:
        """Update an existing distribution configuration."""
        raise NotImplementedError

    async def delete(self, config: Any) -> bool:
        """Delete a distribution configuration by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[dict]:
        """Retrieve all distribution configurations with pagination."""
        raise NotImplementedError
