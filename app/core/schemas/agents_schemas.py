from pydantic import BaseModel


class FlatLabelItem(BaseModel):
    name: str
    value: str
    priority: int


class BestFlatLabelResponse(BaseModel):
    number: list[FlatLabelItem]
