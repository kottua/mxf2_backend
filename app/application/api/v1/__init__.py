from app.application.api.v1.calculations import router as calculations_router
from app.application.api.v1.committed_prices import router as committed_prices_router
from app.application.api.v1.distribution_configs import router as distribution_configs_router
from app.application.api.v1.income_plans import router as income_plans_router
from app.application.api.v1.premises import router as premises_router
from app.application.api.v1.pricing_configs import router as pricing_configs_router
from app.application.api.v1.real_estate_objects import router as real_estate_objects_router
from app.application.api.v1.sales import router as sales_router
from app.application.api.v1.status_mappings import router as status_mappings_router
from fastapi import APIRouter

routers = APIRouter(prefix="/api/v1")

routers.include_router(calculations_router, prefix="/calculate", tags=["Calculations"])
routers.include_router(real_estate_objects_router, prefix="/real-estate-objects", tags=["Real Estate Objects"])
routers.include_router(pricing_configs_router, prefix="/pricing-configs", tags=["Pricing Configs"])
routers.include_router(distribution_configs_router, prefix="/distribution-configs", tags=["Distribution Configs"])
routers.include_router(premises_router, prefix="/premises", tags=["Premises"])
routers.include_router(sales_router, prefix="/sales", tags=["Sales"])
routers.include_router(committed_prices_router, prefix="/committed-prices", tags=["Committed Prices"])
routers.include_router(income_plans_router, prefix="/income-plans", tags=["Income Plans"])
routers.include_router(status_mappings_router, prefix="/status-mappings", tags=["Status Mappings"])
