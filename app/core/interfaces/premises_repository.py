from abc import ABC, abstractmethod
from typing import Any


class PremisesRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> Any:
        """Create a new premises record."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int) -> Any:
        """Retrieve a premises record by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Any]:
        """Retrieve all premises records."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, premises: Any, data: dict) -> Any:
        """Update an existing premises record."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, premises: Any) -> None:
        """Delete a premises record."""
        raise NotImplementedError

    @abstractmethod
    async def create_bulk_premises(self, data: list[dict], reo_id: int) -> Any:
        """Create multiple premises records in bulk."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_recent_premises(self, reo_id: int, limit: int) -> list[Any]:
        """Deactivate all premises associated with a specific REO."""
        raise NotImplementedError
