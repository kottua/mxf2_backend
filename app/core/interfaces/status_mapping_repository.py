from abc import ABC, abstractmethod
from typing import Any


class StatusMappingRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> dict:
        """Create a new status mapping."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int) -> dict:
        """Retrieve a status mapping by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[dict]:
        """Retrieve all status mappings."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, status_mapping: Any, data: dict) -> dict:
        """Update an existing status mapping."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, status_mapping: Any) -> None:
        """Delete a status mapping."""
        raise NotImplementedError
