from pydantic import BaseModel
from typing import Optional


class StatusMappingCreate(BaseModel):
    reo_id: int
    dev_status: str
    sys_status: str

    class Config:
        from_attributes = True

class StatusMappingUpdate(BaseModel):
    reo_id: Optional[int] = None
    dev_status: Optional[str] = None
    sys_status: Optional[str] = None

    class Config:
        from_attributes = True

class StatusMappingResponse(BaseModel):
    id: int
    reo_id: int
    dev_status: str
    sys_status: str

    class Config:
        from_attributes = True
