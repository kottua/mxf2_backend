from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core import exceptions



def handle_object_not_found(_: Request, e: exceptions.ObjectNotFound) -> JSONResponse:
    return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_404_NOT_FOUND)


def handle_object_already_exists(_: Request, e: exceptions.ObjectAlreadyExists) -> JSONResponse:
    return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_409_CONFLICT)

