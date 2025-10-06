
import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.application.api import error_handlers
from app.application.api.v1 import routers

from app.settings import settings
from app.core import exceptions


def _include_router(app: FastAPI) -> None:
    app.include_router(routers)


def _include_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(exceptions.ObjectAlreadyExists, error_handlers.handle_object_already_exists)
    app.add_exception_handler(exceptions.ObjectNotFound, error_handlers.handle_object_not_found)


def create_app() -> FastAPI:
    app = FastAPI()
    _include_router(app)
    _include_error_handlers(app)

    return app


if __name__ == "__main__":
    uvicorn.run("main:create_app", host=settings.HOST, port=settings.PORT)
