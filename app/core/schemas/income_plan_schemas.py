import math
from datetime import datetime
from typing import ClassVar, List, Optional

import pandas as pd
from pydantic import BaseModel, Field, field_validator


class IncomePlanCreate(BaseModel):
    reo_id: int
    property_type: str
    period_begin: datetime
    period_end: datetime
    area: float = Field(..., gt=0)
    planned_sales_revenue: float = Field(..., ge=0)
    price_per_sqm: float = Field(..., ge=0)
    price_per_sqm_end: float = Field(..., ge=0)
    is_active: bool = True

    @field_validator("period_begin", "period_end", mode="before")
    @classmethod
    def parse_date(cls, value: str | datetime) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            raise ValueError(f"Invalid date format: {value}. Expected DD/MM/YYYY or ISO8601.")
        raise TypeError(f"Unsupported type for date: {type(value)}")

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


class IncomePlanFileResponse(BaseModel):
    PREDEFINED_COLUMNS: ClassVar[list[str]] = [
        "Property type",
        "period_begin",
        "period_end",
        "area",
        "planned_sales_revenue",
        "price_per_sqm",
        "price_per_sqm_end",
    ]

    property_type: str = Field(alias="Property type")
    period_begin: str = Field(alias="period_begin")
    period_end: str = Field(alias="period_end")
    area: float = Field(..., gt=0, alias="area")
    planned_sales_revenue: float = Field(..., ge=0, alias="planned_sales_revenue")
    price_per_sqm: float = Field(..., ge=0, alias="price_per_sqm")
    price_per_sqm_end: float = Field(..., ge=0, alias="price_per_sqm_end")

    @field_validator("*", mode="before")
    @classmethod
    def clean_nan_and_empty(cls, value: str | float | int | bool | None) -> str | float | int | bool | None:
        """Convert NaN, None, "nan", "none", and empty strings to None"""
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, str) and value.strip().lower() in {"nan", "none", ""}:
            return None
        return value

    @field_validator("period_begin", "period_end", mode="before")
    @classmethod
    def convert_timestamp(cls, value: str | pd.Timestamp) -> str | pd.Timestamp:
        if isinstance(value, pd.Timestamp):
            return value.strftime("%d/%m/%Y")
        return value


class BulkIncomePlanCreate(BaseModel):
    plans: List[IncomePlanCreate]
