from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field


class CommittedPricesCreate(BaseModel):
    reo_id: int
    pricing_config_id: int
    distribution_config_id: int
    is_active: bool
    actual_price: float = Field(..., ge=0)
    x_rank: float = Field(..., ge=0, le=1)
    content: Dict

    class Config:
        from_attributes = True


class CommittedPricesResponse(BaseModel):
    id: int
    reo_id: int
    pricing_config_id: int
    distribution_config_id: int
    created_at: datetime
    is_active: bool
    actual_price: float
    x_rank: float
    content: Dict

    class Config:
        from_attributes = True


class BulkCommittedPricesCreate(BaseModel):
    commited_prices: list[CommittedPricesCreate]
