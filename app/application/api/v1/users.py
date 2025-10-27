from app.application.api.depends import current_user_deps, user_service_deps
from app.core.schemas.user_schemas import UserInputSchema, UserOutputSchema, UserUpdateSchema
from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.get("/profile", response_model=UserOutputSchema, status_code=status.HTTP_200_OK)
async def profile(user_service: user_service_deps, current_user: current_user_deps) -> UserOutputSchema | None:
    return await user_service.get(email=current_user.email)


@router.post("/", response_model=UserOutputSchema, status_code=status.HTTP_201_CREATED)
async def create_user(user_input: UserInputSchema, user_service: user_service_deps) -> UserOutputSchema:
    user = await user_service.create(user_input=user_input)
    return user


@router.put("/", response_model=UserOutputSchema, status_code=status.HTTP_200_OK)
async def update_user(
    user_input: UserUpdateSchema, user_service: user_service_deps, user: current_user_deps
) -> UserOutputSchema:
    user = await user_service.update(user=user, user_input=user_input)
    return user
