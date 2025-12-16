from abc import ABC, abstractmethod
from typing import Any


class LayoutTypeAttachmentRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> Any:
        """Create a new layout type attachment record."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int) -> Any:
        """Retrieve a layout type attachment record by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_reo_id_and_layout_type(self, reo_id: int, layout_type: str) -> Any:
        """Retrieve a layout type attachment record by reo_id and layout_type."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_by_reo_id(self, reo_id: int) -> list[Any]:
        """Retrieve all layout type attachment records by reo_id."""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Any]:
        """Retrieve all layout type attachment records."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, attachment: Any, data: dict) -> Any:
        """Update an existing layout type attachment record."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, attachment: Any) -> None:
        """Delete a layout type attachment record."""
        raise NotImplementedError
