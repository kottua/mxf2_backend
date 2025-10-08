from abc import ABC, abstractmethod
from typing import Any

from app.core.schemas.real_estate_object_schemas import RealEstateObjectResponse, RealEstateObjectUpdate


class RealEstateObjectRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> RealEstateObjectResponse:
        """Create income plans in bulk."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int) -> Any:
        """Retrieve an income plan by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_full(self, id: int) -> Any:
        """Retrieve an income plan by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[RealEstateObjectResponse]:
        """Retrieve all income plans."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, reo: Any, data: RealEstateObjectUpdate) -> RealEstateObjectResponse:
        """Update an existing income plan."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, reo: Any) -> None:
        """Delete an income plan."""
        raise NotImplementedError
