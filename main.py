import uvicorn
from app.application.api import error_handlers
from app.application.api.v1 import routers
from app.core import exceptions
from app.settings import settings
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


def _include_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def _include_router(app: FastAPI) -> None:
    app.include_router(routers)


def _include_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        exceptions.ObjectAlreadyExists, error_handlers.handle_object_already_exists  # type: ignore
    )
    app.add_exception_handler(exceptions.ObjectNotFound, error_handlers.handle_object_not_found)  # type: ignore
    app.add_exception_handler(
        exceptions.InvalidFileFormatException, error_handlers.handle_invalid_file_format  # type: ignore
    )
    app.add_exception_handler(exceptions.FileReadException, error_handlers.handle_file_read_exception)  # type: ignore
    app.add_exception_handler(
        exceptions.MissingRequiredColumnsException, error_handlers.handle_missing_required_columns  # type: ignore
    )
    app.add_exception_handler(
        exceptions.DataValidationException, error_handlers.handle_data_validation_exception  # type: ignore
    )
    app.add_exception_handler(
        exceptions.FileProcessingException, error_handlers.handle_file_processing_exception  # type: ignore
    )


def create_app() -> FastAPI:
    app = FastAPI()
    _include_middleware(app)
    _include_router(app)
    _include_error_handlers(app)

    return app


if __name__ == "__main__":
    uvicorn.run("main:create_app", host=settings.HOST, port=settings.PORT)
