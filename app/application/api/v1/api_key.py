from app.application.api.depends import auth_service_deps, current_user_deps
from app.core.schemas.user_schemas import ApiTokenSchema
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/create-api-key", status_code=status.HTTP_200_OK)
async def create_api_key(
    payload: ApiTokenSchema, auth_service: auth_service_deps, current_user: current_user_deps
) -> dict:
    api_key = await auth_service.create_api_key(payload=payload, current_user=current_user)
    return api_key


@router.get("/get-api-key", status_code=status.HTTP_200_OK)
async def get_api_key(auth_service: auth_service_deps, current_user: current_user_deps) -> dict | None:
    api_key = await auth_service.api_repository.get_by_user_id(user_id=current_user.id)
    return api_key


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete(current_user: current_user_deps) -> None:
    await auth_service_deps.api_repository.delete_by_user_id(user_id=current_user.id)
