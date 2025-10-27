from app.core.exceptions import ObjectAlreadyExists, ObjectNotFound
from app.core.interfaces.user_repository import UserRepositoryInterface
from app.core.schemas.user_schemas import UserInputSchema, UserOutputSchema
from app.core.utils.security import AuthSecurity
from pydantic import EmailStr


class UserService(AuthSecurity):
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository: UserRepositoryInterface = user_repository

    async def create(self, user_input: UserInputSchema) -> UserOutputSchema:
        user_exists = await self.user_repository.get(email=user_input.email)
        if user_exists:
            raise ObjectAlreadyExists(f"User with this email: {user_input.email} already exists.")

        user_input.password = self.hash_password(password=user_input.password)

        created_user = await self.user_repository.create(user_payload=user_input.model_dump())
        return UserOutputSchema.model_validate(created_user)

    async def get(self, email: EmailStr) -> UserOutputSchema | None:
        response = await self.user_repository.get(email=email)
        if not response:
            raise ObjectNotFound(model_name="User", id_=email)
        return UserOutputSchema.model_validate(response)

    async def update(self, user: UserOutputSchema, user_input: UserInputSchema) -> UserOutputSchema:
        current_user = await self.user_repository.get_by_id(user_id=user.id)
        if not current_user:
            raise ObjectNotFound(model_name="User", id_=user.id)

        response = await self.user_repository.update(user=current_user, updates=user_input.model_dump())
        return UserOutputSchema.model_validate(response)
