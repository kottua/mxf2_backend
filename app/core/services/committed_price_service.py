from app.core.exceptions import ObjectNotFound, ValidationException
from app.core.interfaces.committed_prices_repository import CommittedPricesRepositoryInterface
from app.core.schemas.committed_price_schemas import BulkCommittedPricesCreate, CommittedPricesResponse


class CommittedPricesService:
    def __init__(self, repository: CommittedPricesRepositoryInterface):
        self.repository = repository

    async def create_committed_price(self, data: BulkCommittedPricesCreate) -> list[CommittedPricesResponse]:
        distribution_config_ids = [
            cp.distribution_config_id for cp in data.commited_prices if cp.distribution_config_id
        ]
        pricing_config_ids = [cp.pricing_config_id for cp in data.commited_prices if cp.pricing_config_id]
        reo_ids = [cp.reo_id for cp in data.commited_prices if cp.reo_id]

        if len(set(distribution_config_ids)) > 1:
            raise ValidationException("Всі об'єкти повинні мати однаковий distribution_config_id")

        if len(set(pricing_config_ids)) > 1:
            raise ValidationException("Всі об'єкти повинні мати однаковий pricing_config_id")

        if len(set(reo_ids)) > 1:
            raise ValidationException("Всі об'єкти повинні мати однаковий reo_id")

        distribution_config = await self.repository.exists_distribution_config(config_id=distribution_config_ids[0])
        if not distribution_config:
            raise ObjectNotFound(model_name="DistributionConfig", id_=distribution_config_ids[0])

        pricing_config = await self.repository.exists_pricing_config(config_id=pricing_config_ids[0])
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=pricing_config_ids[0])

        reo_id = await self.repository.exists_reo_id(reo_id=reo_ids[0])
        if not reo_id:
            raise ObjectNotFound(model_name="RealEstateObject", id_=reo_ids[0])

        if all(cp.is_active for cp in data.commited_prices):
            await self.repository.deactivate_active_prices(reo_id=reo_ids[0])

        committed_data = [cp.model_dump() for cp in data.commited_prices]

        committed_prices = await self.repository.create_bulk_committed_prices(data=committed_data, reo_id=reo_ids[0])
        return [CommittedPricesResponse.model_validate(price) for price in committed_prices]

    async def get_committed_price(self, id: int) -> CommittedPricesResponse:
        committed_price = await self.repository.get(id=id)
        if not committed_price:
            raise ObjectNotFound(model_name="CommittedPrices", id_=id)
        return CommittedPricesResponse.model_validate(committed_price)

    async def get_all_committed_prices(self) -> list[CommittedPricesResponse]:
        prices = await self.repository.get_all_committed_prices()
        return [CommittedPricesResponse.model_validate(price) for price in prices]
