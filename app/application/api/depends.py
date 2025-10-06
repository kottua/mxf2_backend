from typing import Annotated

from fastapi import Depends

from app.core.services.committed_price_service import CommittedPricesService
from app.core.services.distribution_config_service import DistributionConfigsService
from app.core.services.income_plan_service import IncomePlanService
from app.infrastructure.repositories.committed_prices_repository import CommittedPricesRepository
from app.infrastructure.repositories.distribution_configs_repository import DistributionConfigsRepository
from app.infrastructure.repositories.income_plans_repository import IncomePlanRepository


def get_company_repository() -> CommittedPricesRepository:
    return CommittedPricesRepository()


def get_commited_service(
        repository: CommittedPricesRepository = Depends(get_company_repository)
) -> CommittedPricesService:
    return CommittedPricesService(repository=repository)


committed_service_deps = Annotated[CommittedPricesService, Depends(get_commited_service)]


def get_distribution_config_repository() -> DistributionConfigsRepository:
    return DistributionConfigsRepository()

def get_distribution_config_service(repository: DistributionConfigsRepository = Depends(get_distribution_config_repository)) -> DistributionConfigsService:
    return DistributionConfigsService(repository=repository)

distribution_config_service_deps = Annotated[DistributionConfigsService, Depends(get_distribution_config_service)]

def get_income_plan_repository() -> IncomePlanRepository:
    return IncomePlanRepository()

def get_income_plan_service(
    repository: IncomePlanRepository = Depends(get_income_plan_repository)
) -> IncomePlanService:
    return IncomePlanService(repository=repository)

income_plan_service_deps = Annotated[IncomePlanService, Depends(get_income_plan_service)]