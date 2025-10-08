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


class FileProcessingException(Exception):
    """Base exception for file processing errors"""

    def __init__(self, message: Optional[str] = "File processing error occurred") -> None:
        super().__init__(message)


class InvalidFileFormatException(FileProcessingException):
    """Raised when uploaded file has invalid format"""

    def __init__(self, message: Optional[str] = "Invalid file format") -> None:
        super().__init__(message)


class FileReadException(FileProcessingException):
    """Raised when file cannot be read"""

    def __init__(self, message: Optional[str] = "Failed to read file") -> None:
        super().__init__(message)


class MissingRequiredColumnsException(FileProcessingException):
    """Raised when required columns are missing from file"""

    def __init__(self, missing_columns: list[str]) -> None:
        self.missing_columns = missing_columns
        message = f"Missing required columns: {', '.join(missing_columns)}"
        super().__init__(message)


class DataValidationException(FileProcessingException):
    """Raised when data validation fails"""

    def __init__(self, row_number: int, error_details: str) -> None:
        self.row_number = row_number
        self.error_details = error_details
        message = f"Validation error in row {row_number}: {error_details}"
        super().__init__(message)
