from pydantic import BaseModel


class ImageData(BaseModel):
    base64: str
    content_type: str
    file_name: str
    size: int

    def to_agent_payload(self) -> list[dict]:
        return [
            {"type": "text", "text": f"Файл: {self.file_name}, размер: {self.size} байт"},
            {"type": "image_url", "image_url": {"url": f"data:{self.content_type};base64,{self.base64}"}},
        ]


class FlatPriorityItem(BaseModel):
    name: str
    values: list[str]
    priority: int


class BestFlatLabelResponse(BaseModel):
    number: list[FlatPriorityItem]


class BestFlatFloorResponse(BaseModel):
    floor: list[FlatPriorityItem]


class LayoutEvaluatorResponse(BaseModel):
    layout_score: list[FlatPriorityItem]
