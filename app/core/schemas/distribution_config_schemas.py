from typing import Optional

from pydantic import BaseModel


class DistributionConfigCreate(BaseModel):
    func_name: str
    content: dict
    is_active: bool = False

    class Config:
        from_attributes = True


class DistributionConfigUpdate(BaseModel):
    func_name: Optional[str] = None
    content: Optional[dict] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class DistributionConfigResponse(BaseModel):
    id: int
    func_name: str
    content: dict
    is_active: bool

    class Config:
        from_attributes = True
