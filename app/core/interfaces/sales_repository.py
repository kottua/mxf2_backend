from abc import ABC, abstractmethod
from typing import Any


class SalesRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> dict:
        """Create a new sales record."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int) -> dict:
        """Retrieve a sales record by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[dict]:
        """Retrieve all sales records."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, sales: Any, data: dict) -> dict:
        """Update a sales record by ID."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, sales: Any) -> bool:
        """Soft delete a sales record by ID."""
        raise NotImplementedError
