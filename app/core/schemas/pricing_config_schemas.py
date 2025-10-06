from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PricingConfigCreate(BaseModel):
    is_active: bool
    reo_id: int
    content: dict

    class Config:
        from_attributes = True

class PricingConfigUpdate(BaseModel):
    is_active: Optional[bool] = None
    content: Optional[dict] = None

    class Config:
        from_attributes = True

class PricingConfigResponse(BaseModel):
    id: int
    is_active: bool
    reo_id: int
    created: datetime
    updated: datetime
    content: dict

    class Config:
        from_attributes = True