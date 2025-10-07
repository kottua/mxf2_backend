from app.core.exceptions import ObjectNotFound
from app.core.interfaces.committed_prices_repository import CommittedPricesRepositoryInterface
from app.core.schemas.committed_price_schemas import CommittedPricesCreate, CommittedPricesResponse


class CommittedPricesService:
    def __init__(self, repository: CommittedPricesRepositoryInterface):
        self.repository = repository

    async def create_committed_price(self, data: CommittedPricesCreate) -> CommittedPricesResponse:
        distribution_config = await self.repository.exists_distribution_config(config_id=data.distribution_config_id)
        if not distribution_config:
            raise ObjectNotFound(model_name="DistributionConfig", id_=data.distribution_config_id)

        pricing_config = await self.repository.exists_pricing_config(config_id=data.pricing_config_id)
        if not pricing_config:
            raise ObjectNotFound(model_name="PricingConfig", id_=data.pricing_config_id)

        reo_id = await self.repository.exists_reo_id(reo_id=data.reo_id)
        if not reo_id:
            raise ObjectNotFound(model_name="RealEstateObject", id_=data.reo_id)

        if data.is_active:
            await self.repository.deactivate_active_prices(reo_id=data.reo_id)
        committed_price = await self.repository.create(data.model_dump())
        return CommittedPricesResponse.model_validate(committed_price)

    async def get_committed_price(self, id: int) -> CommittedPricesResponse:
        committed_price = await self.repository.get(id=id)
        if not committed_price:
            raise ObjectNotFound(model_name="CommittedPrices", id_=id)
        return CommittedPricesResponse.model_validate(committed_price)

    async def get_all_committed_prices(self) -> list[CommittedPricesResponse]:
        prices = await self.repository.get_all_committed_prices()
        return [CommittedPricesResponse.model_validate(price) for price in prices]
