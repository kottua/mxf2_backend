
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime




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

class BulkPremisesCreateRequest(BaseModel):
    premises: List[PremisesCreate]