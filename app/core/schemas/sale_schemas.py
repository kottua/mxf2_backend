from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class SalesCreate(BaseModel):
    premises_id: int
    saledate: datetime
    amount: float = Field(..., ge=0)
    notified_at: Optional[datetime] = None
    is_deleted: bool = False

    class Config:
        from_attributes = True

class SalesUpdate(BaseModel):
    premises_id: Optional[int] = None
    saledate: Optional[datetime] = None
    amount: Optional[float] = Field(None, ge=0)
    notified_at: Optional[datetime] = None
    is_deleted: Optional[bool] = None

    class Config:
        from_attributes = True

class SalesResponse(BaseModel):
    id: int
    premises_id: int
    saledate: datetime
    amount: float
    notified_at: Optional[datetime]
    is_deleted: bool

    class Config:
        from_attributes = True
