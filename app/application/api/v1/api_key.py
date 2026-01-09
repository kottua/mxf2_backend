from app.application.api.depends import auth_service_deps, current_user_deps
from app.core.exceptions import ObjectNotFound
from app.core.schemas.user_schemas import ApiTokenInputSchema, ApiTokenOutputSchema
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.post("/create-api-key", status_code=status.HTTP_200_OK, response_model=ApiTokenOutputSchema)
async def create_api_key(
    payload: ApiTokenInputSchema, auth_service: auth_service_deps, current_user: current_user_deps
) -> ApiTokenOutputSchema:
    api_key = await auth_service.create_api_key(payload=payload, current_user=current_user)
    return api_key


@router.get("/get-api-key", status_code=status.HTTP_200_OK)
async def get_api_key(auth_service: auth_service_deps, current_user: current_user_deps) -> ApiTokenOutputSchema:
    api_key = await auth_service.api_repository.get_by_user_id(user_id=current_user.id)
    if not api_key:
        raise ObjectNotFound(model_name="ApiToken", id_=current_user.id)
    return ApiTokenOutputSchema(key_name=api_key.key_name, access_token=api_key.key_value)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete(current_user: current_user_deps, auth_service: auth_service_deps) -> None:
    await auth_service.api_repository.delete_by_user_id(user_id=current_user.id)
