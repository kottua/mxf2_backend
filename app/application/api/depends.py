from typing import Annotated

from app.core.schemas.user_schemas import UserOutputSchema
from app.core.services.agent_service import AgentService
from app.core.services.auth_service import AuthService
from app.core.services.committed_price_service import CommittedPricesService
from app.core.services.distribution_config_service import DistributionConfigsService
from app.core.services.file_processing_service import FileProcessingService
from app.core.services.income_plan_service import IncomePlanService
from app.core.services.layout_type_attachment_service import LayoutTypeAttachmentService
from app.core.services.premises_service import PremisesService
from app.core.services.pricing_config_service import PricingConfigService
from app.core.services.real_estate_object_service import RealEstateObjectService
from app.core.services.sales_service import SalesService
from app.core.services.scoring_calculation_service import ScoringCalculationService
from app.core.services.status_mapping_service import StatusMappingService
from app.core.services.user_service import UserService
from app.infrastructure.agents.agent_manager import AgentManager
from app.infrastructure.excel.excel_processor import ExcelProcessor
from app.infrastructure.repositories.committed_prices_repository import CommittedPricesRepository
from app.infrastructure.repositories.distribution_configs_repository import DistributionConfigsRepository
from app.infrastructure.repositories.income_plans_repository import IncomePlanRepository
from app.infrastructure.repositories.layout_type_attachment_repository import LayoutTypeAttachmentRepository
from app.infrastructure.repositories.premises_repository import PremisesRepository
from app.infrastructure.repositories.pricing_config_repository import PricingConfigRepository
from app.infrastructure.repositories.real_estate_object_repository import RealEstateObjectRepository
from app.infrastructure.repositories.sales_repository import SalesRepository
from app.infrastructure.repositories.status_mapping_repository import StatusMappingRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.settings import AgentConfig, settings
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

http_bearer = HTTPBearer()


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository=user_repository)


def get_auth_service(user_repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repository=user_repository)


auth_service_deps = Annotated[AuthService, Depends(get_auth_service)]
token_deps = Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]


async def get_current_user(auth_service: auth_service_deps, token: token_deps) -> UserOutputSchema:
    return await auth_service.get_current_user(token.credentials)


current_user_deps = Annotated[UserOutputSchema, Depends(get_current_user)]
user_service_deps = Annotated[UserService, Depends(get_user_service)]


def get_commited_repository() -> CommittedPricesRepository:
    return CommittedPricesRepository()


def get_commited_service(
    repository: CommittedPricesRepository = Depends(get_commited_repository),
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
    distribution_repository: DistributionConfigsRepository = Depends(get_distribution_config_repository),
    reo_repository: RealEstateObjectRepository = Depends(get_real_estate_object_repository),
    premises_repository: PremisesRepository = Depends(get_premises_repository),
    committed_prices_repository: CommittedPricesRepository = Depends(get_commited_repository),
) -> FileProcessingService:
    return FileProcessingService(
        file_processor=file_processor,
        distribution_repository=distribution_repository,
        reo_repository=reo_repository,
        premises_repository=premises_repository,
        committed_prices_repository=committed_prices_repository,
    )


def get_scoring_service(
    reo_repository: RealEstateObjectRepository = Depends(get_real_estate_object_repository),
    distribution_config_repository: DistributionConfigsRepository = Depends(get_distribution_config_repository),
) -> ScoringCalculationService:
    return ScoringCalculationService(
        reo_repository=reo_repository, distribution_config_repository=distribution_config_repository
    )


def get_agent_config() -> AgentConfig:
    return settings.agent


def get_agent_manager(config: AgentConfig = Depends(get_agent_config)) -> AgentManager:
    return AgentManager(config=config)


agent_manager_deps = Annotated[AgentManager, Depends(get_agent_manager)]


def get_agent_service(
    agent_manager: AgentManager = Depends(get_agent_manager),
    real_estate_object_service: RealEstateObjectService = Depends(get_real_estate_object_service),
    pricing_config_service: PricingConfigService = Depends(get_pricing_config_service),
) -> AgentService:
    return AgentService(
        agent_manager=agent_manager,
        real_estate_object_service=real_estate_object_service,
        pricing_config_service=pricing_config_service,
    )


agent_service_deps = Annotated[AgentService, Depends(get_agent_service)]


committed_service_deps = Annotated[CommittedPricesService, Depends(get_commited_service)]
distribution_config_service_deps = Annotated[DistributionConfigsService, Depends(get_distribution_config_service)]
file_processing_service_deps = Annotated[FileProcessingService, Depends(get_file_processing_service)]
real_estate_object_service_deps = Annotated[RealEstateObjectService, Depends(get_real_estate_object_service)]
income_plan_service_deps = Annotated[IncomePlanService, Depends(get_income_plan_service)]
premises_service_deps = Annotated[PremisesService, Depends(get_premises_service)]


def get_layout_type_attachment_repository() -> LayoutTypeAttachmentRepository:
    return LayoutTypeAttachmentRepository()


def get_layout_type_attachment_service(
    repository: LayoutTypeAttachmentRepository = Depends(get_layout_type_attachment_repository),
) -> LayoutTypeAttachmentService:
    return LayoutTypeAttachmentService(repository=repository)


layout_type_attachment_service_deps = Annotated[
    LayoutTypeAttachmentService, Depends(get_layout_type_attachment_service)
]
status_mapping_service_deps = Annotated[StatusMappingService, Depends(get_status_mapping_service)]
sales_service_deps = Annotated[SalesService, Depends(get_sales_service)]
pricing_config_service_deps = Annotated[PricingConfigService, Depends(get_pricing_config_service)]
scoring_service_deps = Annotated[ScoringCalculationService, Depends(get_scoring_service)]
