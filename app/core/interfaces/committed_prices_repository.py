from abc import ABC, abstractmethod


class CommittedPricesRepositoryInterface(ABC):

    @abstractmethod
    async def create(self, data: dict) -> dict:
        """Create a new committed price record."""
        raise NotImplementedError

    @abstractmethod
    async def create_bulk_committed_prices(self, data: list[dict], reo_id: int) -> list[dict]:
        """Create multiple committed price records in bulk."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: int) -> dict:
        """Get a committed price record by its ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_reo_and_distribution_config(
        self, reo_id: int, distribution_config_id: int, is_active: bool
    ) -> list[dict]:
        """Get committed price records by REO ID and distribution configuration ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_committed_prices(self) -> list[dict]:
        """Get all committed price records."""
        raise NotImplementedError

    @abstractmethod
    async def deactivate_active_prices(self, reo_id: int) -> None:
        """Deactivate existing committed price records for a given REO ID."""
        raise NotImplementedError

    async def exists_distribution_config(self, config_id: int) -> bool:
        """Check if a distribution configuration exists by its ID."""
        raise NotImplementedError

    async def exists_pricing_config(self, config_id: int) -> bool:
        """Check if a pricing configuration exists by its ID."""
        raise NotImplementedError

    async def exists_reo_id(self, reo_id: int) -> bool:
        """Check if a REO ID exists."""
        raise NotImplementedError
