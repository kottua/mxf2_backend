import math
from datetime import datetime
from typing import ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class PremisesCreate(BaseModel):
    reo_id: int
    property_type: str
    premises_id: str
    number_of_unit: int
    number: int
    entrance: str
    floor: int
    layout_type: str
    full_price: Optional[float] = None
    total_area_m2: float
    estimated_area_m2: float
    price_per_meter: Optional[float] = None
    number_of_rooms: Optional[int] = None
    living_area_m2: Optional[float] = None
    kitchen_area_m2: Optional[float] = None
    view_from_window: Optional[str] = None
    number_of_levels: Optional[int] = None
    number_of_loggias: Optional[int] = None
    number_of_balconies: Optional[int] = None
    number_of_bathrooms_with_toilets: Optional[int] = None
    number_of_separate_bathrooms: Optional[int] = None
    number_of_terraces: Optional[int] = None
    studio: bool = False
    status: str
    sales_amount: Optional[float] = None
    customcontent: Optional[Dict] = None

    class Config:
        from_attributes = True


class PremisesUpdate(BaseModel):
    property_type: Optional[str] = None
    premises_id: Optional[str] = None
    number_of_unit: Optional[int] = None
    number: Optional[int] = None
    entrance: Optional[str] = None
    floor: Optional[int] = Field(None, ge=-20, le=200)
    layout_type: Optional[str] = None
    full_price: Optional[float] = None
    total_area_m2: Optional[float] = Field(None, gt=0)
    estimated_area_m2: Optional[float] = Field(None, gt=0)
    price_per_meter: Optional[float] = Field(None, gt=0)
    number_of_rooms: Optional[int] = Field(None, ge=0)
    living_area_m2: Optional[float] = Field(None, ge=0)
    kitchen_area_m2: Optional[float] = Field(None, ge=0)
    view_from_window: Optional[str] = None
    number_of_levels: Optional[int] = Field(None, ge=0)
    number_of_loggias: Optional[int] = Field(None, ge=0)
    number_of_balconies: Optional[int] = Field(None, ge=0)
    number_of_bathrooms_with_toilets: Optional[int] = Field(None, ge=0)
    number_of_separate_bathrooms: Optional[int] = Field(None, ge=0)
    number_of_terraces: Optional[int] = Field(None, ge=0)
    studio: Optional[bool] = None
    status: Optional[str] = None
    sales_amount: Optional[float] = Field(None, ge=0)
    customcontent: Optional[Dict] = None

    class Config:
        from_attributes = True


class PremisesResponse(BaseModel):
    id: int
    reo_id: int
    uploaded: datetime
    property_type: str
    premises_id: str
    number_of_unit: int
    number: int
    entrance: str
    floor: int
    layout_type: str
    full_price: Optional[float]
    total_area_m2: float
    estimated_area_m2: float
    price_per_meter: float
    number_of_rooms: int
    living_area_m2: Optional[float]
    kitchen_area_m2: Optional[float]
    view_from_window: Optional[str]
    number_of_levels: Optional[int]
    number_of_loggias: Optional[int]
    number_of_balconies: Optional[int]
    number_of_bathrooms_with_toilets: Optional[int]
    number_of_separate_bathrooms: Optional[int]
    number_of_terraces: Optional[int]
    studio: bool
    status: str
    sales_amount: Optional[float]
    customcontent: Optional[Dict]

    class Config:
        from_attributes = True


class PremisesFileSpecificationResponse(BaseModel):
    PREDEFINED_COLUMNS: ClassVar[list[str]] = [
        "Property type",
        "Premises ID",
        "Number of unit",
        "Number",
        "Entrance",
        "Floor",
        "Layout type",
        "Full price",
        "Total area, m2",
        "Estimated area, m2",
        "Price per meter",
        "Number of rooms",
        "Living area, m2",
        "Kitchen area, m2",
        "View from window",
        "Number of levels",
        "Number of loggias",
        "Number of balconies",
        "Number of bathrooms with toilets",
        "Number of separate bathrooms",
        "Number of terraces",
        "Studio",
        "Status",
        "Sales amount",
    ]

    property_type: str = Field(alias="Property type")
    premises_id: Optional[str] = Field(alias="Premises ID", default=None)
    number_of_unit: int = Field(alias="Number of unit")
    number: int = Field(alias="Number")
    entrance: int = Field(alias="Entrance")
    floor: int = Field(alias="Floor")
    layout_type: str = Field(alias="Layout type")
    full_price: Optional[float] = Field(alias="Full price", default=None)
    total_area_m2: float = Field(alias="Total area, m2")
    estimated_area_m2: float = Field(alias="Estimated area, m2")
    price_per_meter: Optional[float] = Field(alias="Price per meter", default=None)
    number_of_rooms: Optional[int] = Field(alias="Number of rooms")
    living_area_m2: Optional[float] = Field(alias="Living area, m2", default=None)
    kitchen_area_m2: Optional[float] = Field(alias="Kitchen area, m2", default=None)
    view_from_window: Optional[str] = Field(alias="View from window", default=None)
    number_of_levels: Optional[int] = Field(alias="Number of levels", default=None)
    number_of_loggias: Optional[int] = Field(alias="Number of loggias", default=None)
    number_of_balconies: Optional[int] = Field(alias="Number of balconies", default=None)
    number_of_bathrooms_with_toilets: Optional[int] = Field(alias="Number of bathrooms with toilets", default=None)
    number_of_separate_bathrooms: Optional[int] = Field(alias="Number of separate bathrooms", default=None)
    number_of_terraces: Optional[int] = Field(alias="Number of terraces", default=None)
    studio: bool = Field(alias="Studio", default=False)
    status: str = Field(alias="Status")
    sales_amount: Optional[float] = Field(alias="Sales amount", default=None)
    customcontent: Optional[Dict] = None

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

    @field_validator("studio", mode="before")
    @classmethod
    def validate_date_format(cls, value: str) -> bool:
        """Convert various representations of boolean to actual bool"""
        try:
            if value in ["Yes", 1, "1", "yes", "true", True, "да", "Да"]:
                return True
            return False
        except ValueError:
            raise ValueError(f"Invalid boolean format: '{value}'. Expected Yes/No or 1/0 or true/false or да/нет.")

    @model_validator(mode="after")
    def generate_premises_id(self) -> "PremisesFileSpecificationResponse":
        """Generate premises_id if it's None"""
        if not self.premises_id:
            self.premises_id = f"SV/A/{self.floor}/{self.number_of_unit}/{self.layout_type}/{self.number}"
        return self

    @classmethod
    def custom_model_validate(cls, row: dict) -> "PremisesFileSpecificationResponse":
        """
        Custom method to validate a row dict, separating predefined and custom fields.
        """
        custom = {k: v for k, v in row.items() if k not in cls.PREDEFINED_COLUMNS}
        data = {k: v for k, v in row.items() if k in cls.PREDEFINED_COLUMNS}
        instance = cls.model_validate(data)
        instance.customcontent = custom or None
        return instance


class BulkPremisesCreateRequest(BaseModel):
    premises: List[PremisesCreate]
