from typing import Annotated

from app.core.services.committed_price_service import CommittedPricesService
from app.core.services.distribution_config_service import DistributionConfigsService
from app.core.services.file_processing_service import FileProcessingService
from app.core.services.income_plan_service import IncomePlanService
from app.core.services.premises_service import PremisesService
from app.core.services.pricing_config_service import PricingConfigService
from app.core.services.real_estate_object_service import RealEstateObjectService
from app.core.services.sales_service import SalesService
from app.core.services.scoring_calculation_service import ScoringCalculationService
from app.core.services.status_mapping_service import StatusMappingService
from app.infrastructure.excel.excel_processor import ExcelProcessor
from app.infrastructure.repositories.committed_prices_repository import CommittedPricesRepository
from app.infrastructure.repositories.distribution_configs_repository import DistributionConfigsRepository
from app.infrastructure.repositories.income_plans_repository import IncomePlanRepository
from app.infrastructure.repositories.premises_repository import PremisesRepository
from app.infrastructure.repositories.pricing_config_repository import PricingConfigRepository
from app.infrastructure.repositories.real_estate_object_repository import RealEstateObjectRepository
from app.infrastructure.repositories.sales_repository import SalesRepository
from app.infrastructure.repositories.status_mapping_repository import StatusMappingRepository
from fastapi import Depends


def get_company_repository() -> CommittedPricesRepository:
    return CommittedPricesRepository()


def get_commited_service(
    repository: CommittedPricesRepository = Depends(get_company_repository),
) -> CommittedPricesService:
    return CommittedPricesService(repository=repository)


def get_distribution_config_repository() -> DistributionConfigsRepository:
    return DistributionConfigsRepository()


def get_distribution_config_service(
    repository: DistributionConfigsRepository = Depends(get_distribution_config_repository),
) -> DistributionConfigsService:
    return DistributionConfigsService(repository=repository)


def get_real_estate_object_repository() -> RealEstateObjectRepository:
    return RealEstateObjectRepository()


def get_real_estate_object_service(
    repository: RealEstateObjectRepository = Depends(get_real_estate_object_repository),
) -> RealEstateObjectService:
    return RealEstateObjectService(repository=repository)


def get_income_plan_repository() -> IncomePlanRepository:
    return IncomePlanRepository()


def get_income_plan_service(
    repository: IncomePlanRepository = Depends(get_income_plan_repository),
    reo_repository: RealEstateObjectRepository = Depends(get_real_estate_object_repository),
) -> IncomePlanService:
    return IncomePlanService(repository=repository, reo_repository=reo_repository)


def get_premises_repository() -> PremisesRepository:
    return PremisesRepository()


def get_premises_service(
    repository: PremisesRepository = Depends(get_premises_repository),
    reo_repository: RealEstateObjectRepository = Depends(get_real_estate_object_repository),
) -> PremisesService:
    return PremisesService(repository=repository, reo_repository=reo_repository)


def get_status_mapping_repository() -> StatusMappingRepository:
    return StatusMappingRepository()


def get_status_mapping_service(
    repository: StatusMappingRepository = Depends(get_status_mapping_repository),
) -> StatusMappingService:
    return StatusMappingService(repository=repository)


def get_sales_repository() -> SalesRepository:
    return SalesRepository()


def get_sales_service(
    repository: SalesRepository = Depends(get_sales_repository),
) -> SalesService:
    return SalesService(repository=repository)


def get_pricing_config_repository() -> PricingConfigRepository:
    return PricingConfigRepository()


def get_pricing_config_service(
    repository: PricingConfigRepository = Depends(get_pricing_config_repository),
) -> PricingConfigService:
    return PricingConfigService(repository=repository)


def get_excel_processor() -> ExcelProcessor:
    return ExcelProcessor()


def get_file_processing_service(
    file_processor: ExcelProcessor = Depends(get_excel_processor),
) -> FileProcessingService:
    return FileProcessingService(file_processor=file_processor)


def get_scoring_service(
    reo_repository: RealEstateObjectRepository = Depends(get_real_estate_object_repository),
    distribution_config_repository: DistributionConfigsRepository = Depends(get_distribution_config_repository),
) -> ScoringCalculationService:
    return ScoringCalculationService(
        reo_repository=reo_repository, distribution_config_repository=distribution_config_repository
    )


committed_service_deps = Annotated[CommittedPricesService, Depends(get_commited_service)]
distribution_config_service_deps = Annotated[DistributionConfigsService, Depends(get_distribution_config_service)]
file_processing_service_deps = Annotated[FileProcessingService, Depends(get_file_processing_service)]
real_estate_object_service_deps = Annotated[RealEstateObjectService, Depends(get_real_estate_object_service)]
income_plan_service_deps = Annotated[IncomePlanService, Depends(get_income_plan_service)]
premises_service_deps = Annotated[PremisesService, Depends(get_premises_service)]
status_mapping_service_deps = Annotated[StatusMappingService, Depends(get_status_mapping_service)]
sales_service_deps = Annotated[SalesService, Depends(get_sales_service)]
pricing_config_service_deps = Annotated[PricingConfigService, Depends(get_pricing_config_service)]
scoring_service_deps = Annotated[ScoringCalculationService, Depends(get_scoring_service)]
