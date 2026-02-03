from typing import Optional

from app.core.utils.enums import ConfigStatus
from pydantic import BaseModel


class DistributionConfigCreate(BaseModel):
    func_name: str
    content: dict
    is_active: bool = True
    config_status: ConfigStatus = ConfigStatus.CUSTOM

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
    config_status: ConfigStatus

    class Config:
        from_attributes = True
