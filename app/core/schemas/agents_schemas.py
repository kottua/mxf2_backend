import base64
import io
from enum import StrEnum
from typing import Any, Dict

from openai import OpenAI
from pydantic import BaseModel, Field, PrivateAttr


class FilesData(BaseModel):
    layout_type: str | None = None
    view_from_window: str | None = None
    base64: str
    content_type: str
    file_name: str
    size: int

    _file_bytes: bytes = PrivateAttr()
    _file_obj: io.BytesIO = PrivateAttr()

    def model_post_init(self, context: Any) -> None:
        self._file_bytes = base64.b64decode(self.base64)
        self._file_obj = io.BytesIO(self._file_bytes)
        self._file_obj.name = self.file_name

    def _pdf_payload(self, file_id: str) -> list[dict]:
        descriptor = self.layout_type or self.view_from_window

        return [
            {
                "type": "text",
                "text": (f"PDF file attached: {self.file_name}, " f"size: {self.size}, descriptor: {descriptor}"),
            },
            {
                "type": "file",
                "file": {
                    "file_id": file_id,
                },
            },
        ]

    def _image_payload(self) -> list[dict]:
        descriptor = self.layout_type or self.view_from_window
        return [
            {
                "type": "text",
                "text": (f"Image name: {self.file_name}, " f"size: {self.size}, descriptor: {descriptor}"),
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:{self.content_type};base64,{self.base64}"},
            },
        ]

    def upload_and_get_payload(self, client: "OpenAI") -> list[dict]:
        """
        Загружает файл через API (если необходимо) и возвращает payload для OpenAI.
        Для PDF файлов загружает через API, для изображений использует base64 напрямую.
        """
        if self.content_type == "application/pdf":
            uploaded_file = client.files.create(file=self._file_obj, purpose="assistants")
            return self._pdf_payload(uploaded_file.id)

        return self._image_payload()


class FlatPriorityItem(BaseModel):
    name: str
    values: list[str]
    priority: int


class BestFlatLabelResponse(BaseModel):
    number: list[FlatPriorityItem]


class BestFlatFloorResponse(BaseModel):
    floor: list[FlatPriorityItem]


class LayoutEvaluatorResponse(BaseModel):
    layout_type: list[FlatPriorityItem]


class WindowViewEvaluatorResponse(BaseModel):
    view_from_window: list[FlatPriorityItem]


class TotalAreaEvaluatorResponse(BaseModel):
    total_area_m2: list[FlatPriorityItem]


class EntranceEvaluatorResponse(BaseModel):
    entrance: list[FlatPriorityItem]


class RoomEvaluatorResponse(BaseModel):
    number_of_rooms: list[FlatPriorityItem]


class ValidAgentFields(StrEnum):
    NUMBER = "number"
    FLOOR = "floor"
    LAYOUT_TYPE = "layout_type"
    VIEW_FROM_WINDOW = "view_from_window"
    TOTAL_AREA_M2 = "total_area_m2"
    ENTRANCE = "entrance"
    NUMBER_OF_ROOMS = "number_of_rooms"

    @classmethod
    def list_values(cls) -> list[str]:
        """Повертає список всіх значень: ['number', 'floor', ...]"""
        return [member.value for member in cls]

    @classmethod
    def to_prompt_string(cls) -> str:
        """Повертає рядок для промпту: 'number, floor, layout_type, ...'"""
        return ", ".join([member.value for member in cls])


class DynamicConfig(BaseModel):
    importantFields: Dict[ValidAgentFields, bool] = Field(..., description="Вказує, чи є поле важливим.")

    weights: Dict[ValidAgentFields, float] = Field(..., description="Ваги факторів. Сума має бути 1.0.")


class WeightedFactorsResponse(BaseModel):
    dynamicConfig: DynamicConfig
