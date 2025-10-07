from datetime import datetime
from typing import List, Optional

from app.core.schemas.income_plan_schemas import IncomePlanResponse
from app.core.schemas.premise_schemas import PremisesResponse
from app.core.schemas.pricing_config_schemas import PricingConfigResponse
from pydantic import BaseModel, Field


class RealEstateObjectCreate(BaseModel):
    name: str
    lon: Optional[float] = Field(None, ge=-180, le=180)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    curr: Optional[str] = None
    url: Optional[str] = None
    custom_fields: Optional[dict] = None

    class Config:
        from_attributes = True


class RealEstateObjectUpdate(BaseModel):
    name: Optional[str] = None
    lon: Optional[float] = Field(None, ge=-180, le=180)
    lat: Optional[float] = Field(None, ge=-90, le=90)
    curr: Optional[str] = None
    url: Optional[str] = None
    is_deleted: Optional[bool] = None
    custom_fields: Optional[dict] = None

    class Config:
        from_attributes = True


class RealEstateObjectResponse(BaseModel):
    id: int
    name: str
    lon: Optional[float]
    lat: Optional[float]
    curr: Optional[str]
    url: Optional[str]
    created: datetime
    updated: datetime
    is_deleted: bool
    custom_fields: Optional[dict]

    class Config:
        from_attributes = True


class RealEstateObjectFullResponse(BaseModel):
    id: int
    name: str
    lon: Optional[float]
    lat: Optional[float]
    curr: Optional[str]
    url: Optional[str]
    created: datetime
    updated: datetime
    is_deleted: bool
    custom_fields: Optional[dict]

    premises: List[PremisesResponse]
    income_plans: List[IncomePlanResponse]
    pricing_configs: List[PricingConfigResponse]

    class Config:
        from_attributes = True
