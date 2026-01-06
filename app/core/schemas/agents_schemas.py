import base64
import io
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field


class FilesData(BaseModel):
    layout_type: str
    base64: str
    content_type: str
    file_name: str
    size: int

    _file_bytes: bytes = Field(default=None, exclude=True, repr=False)
    _file_obj: io.BytesIO = Field(default=None, exclude=True, repr=False)

    def model_post_init(self, context: Any) -> None:
        self._file_bytes = base64.b64decode(self.base64)
        self._file_obj = io.BytesIO(self._file_bytes)
        self._file_obj.name = self.file_name

    def _pdf_payload(self, file_id: str) -> list[dict]:
        return [
            {
                "type": "text",
                "text": (
                    f"PDF file attached: {self.file_name}, " f"size: {self.size}, " f"layout_type: {self.layout_type}"
                ),
            },
            {
                "type": "file",
                "file": {
                    "file_id": file_id,
                },
            },
        ]

    def _image_payload(self) -> list[dict]:
        return [
            {
                "type": "text",
                "text": (f"Image name: {self.file_name}, " f"size: {self.size}, " f"layout_type: {self.layout_type}"),
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
