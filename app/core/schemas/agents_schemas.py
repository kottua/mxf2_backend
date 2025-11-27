from pydantic import BaseModel


class FlatPriorityItem(BaseModel):
    name: str
    value: list[str]
    priority: int


class BestFlatLabelResponse(BaseModel):
    number: list[FlatPriorityItem]
