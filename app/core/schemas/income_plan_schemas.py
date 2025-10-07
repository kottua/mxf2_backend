from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class IncomePlanCreate(BaseModel):
    reo_id: int
    property_type: str
    period_begin: str
    period_end: str
    area: float = Field(..., gt=0)
    planned_sales_revenue: float = Field(..., ge=0)
    price_per_sqm: float = Field(..., ge=0)
    price_per_sqm_end: float = Field(..., ge=0)
    is_active: bool = True

    @field_validator("period_begin", "period_end", mode="before")
    def validate_date_format(cls, value: str) -> str:
        try:
            datetime.strptime(value, "%d/%m/%Y")
            return value
        except ValueError:
            raise ValueError(f"Invalid date format: '{value}'. Expected DD/MM/YYYY.")

    class Config:
        from_attributes = True


class IncomePlanUpdate(BaseModel):
    reo_id: Optional[int] = None
    property_type: Optional[str] = None
    period_begin: Optional[str] = None
    period_end: Optional[str] = None
    area: Optional[float] = Field(None, gt=0)
    planned_sales_revenue: Optional[float] = Field(None, ge=0)
    price_per_sqm: Optional[float] = Field(None, ge=0)
    price_per_sqm_end: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None

    class Config:
        from_attributes = True


class IncomePlanResponse(BaseModel):
    id: int
    uploaded_at: datetime
    is_active: bool
    reo_id: int
    property_type: str
    period_begin: datetime
    period_end: datetime
    area: float
    planned_sales_revenue: float
    price_per_sqm: float
    price_per_sqm_end: float
    is_deleted: bool

    class Config:
        from_attributes = True


class BulkIncomePlanCreate(BaseModel):
    plans: List[IncomePlanCreate]
