from typing import Any, Optional


class ObjectAlreadyExists(Exception):
    def __init__(self, message: Optional[str] = ""):
        super().__init__(message)


class ObjectNotFound(Exception):
    def __init__(self, model_name: str, id_: Any) -> None:
        self.msg = f"{model_name} with given identifier - {id_} not found"
        super().__init__(self.msg)


class ValidationException(Exception):
    def __init__(self, message: Optional[str] = "Validation error occurred") -> None:
        super().__init__(message)