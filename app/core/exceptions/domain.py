from typing import Any, Optional


class ObjectAlreadyExists(Exception):
    def __init__(self, message: Optional[str] = ""):
        super().__init__(message)


class ObjectNotFound(Exception):
    def __init__(self, model_name: str, id_: Any) -> None:
        self.msg = f"{model_name} with given identifier - {id_} not found"
        super().__init__(self.msg)


class InvalidCredentials(Exception):
    def __init__(self, message: Optional[str] = "Invalid credentials provided") -> None:
        super().__init__(message)


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


class AgentException(Exception):
    """Base exception for agent-related errors"""

    def __init__(self, message: Optional[str] = "Agent error occurred") -> None:
        super().__init__(message)


class AgentNotFound(AgentException):
    """Raised when agent is not found or not registered"""

    def __init__(self, agent_id: str) -> None:
        message = f"Agent with id '{agent_id}' not found. Please register the agent first."
        super().__init__(message)


class AgentExecutionError(AgentException):
    """Raised when agent execution fails"""

    def __init__(self, agent_id: str, reason: Optional[str] = None) -> None:
        message = f"Failed to run agent '{agent_id}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)
