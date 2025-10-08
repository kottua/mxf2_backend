from app.core import exceptions
from fastapi import Request, status
from fastapi.responses import JSONResponse


def handle_object_not_found(_: Request, e: exceptions.ObjectNotFound) -> JSONResponse:
    return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_404_NOT_FOUND)


def handle_object_already_exists(_: Request, e: exceptions.ObjectAlreadyExists) -> JSONResponse:
    return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_409_CONFLICT)


def handle_invalid_file_format(_: Request, e: exceptions.InvalidFileFormatException) -> JSONResponse:
    return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


def handle_file_read_exception(_: Request, e: exceptions.FileReadException) -> JSONResponse:
    return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


def handle_missing_required_columns(_: Request, e: exceptions.MissingRequiredColumnsException) -> JSONResponse:
    return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)


def handle_data_validation_exception(_: Request, e: exceptions.DataValidationException) -> JSONResponse:
    return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def handle_file_processing_exception(_: Request, e: exceptions.FileProcessingException) -> JSONResponse:
    return JSONResponse(
        content={"message": f"File processing error: {str(e)}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
