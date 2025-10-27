from app.core.exceptions import InvalidCredentials, ObjectNotFound
from app.core.interfaces.user_repository import UserRepositoryInterface
from app.core.schemas.auth_schemas import TokenSchema, TokenType
from app.core.schemas.user_schemas import UserOutputSchema
from app.core.utils.security import AuthSecurity
from app.settings import settings
from pydantic import EmailStr


class AuthService(AuthSecurity):
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository: UserRepositoryInterface = user_repository

    async def get_current_user(self, token: str) -> UserOutputSchema:
        verify = self.verify_token(token=token, token_type=TokenType.ACCESS)
        if not verify:
            raise InvalidCredentials("Invalid or expired access token")
        payload = self.decode_token(
            token=token, key=settings.token.SECRET_KEY, algorithms=[settings.token.ALGORITHM], options={}
        )
        email = payload.get("sub")
        if not email:
            raise InvalidCredentials("Invalid token")
        user = await self.user_repository.get(email)
        if not user:
            raise ObjectNotFound("User", email)
        return UserOutputSchema.model_validate(user)

    def generate_tokens_for_user(self, user: UserOutputSchema) -> TokenSchema:
        access_token = self.create_token(
            payload={"sub": user.email},
            token_type=TokenType.ACCESS,
            expire_minutes=settings.token.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        refresh_token = self.create_token(
            payload={"sub": user.email},
            token_type=TokenType.REFRESH,
            expire_minutes=settings.token.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

        return TokenSchema(
            access_token=access_token, refresh_token=refresh_token, token_type=settings.token.TOKEN_TYPE
        )

    async def login(self, email: EmailStr, password: str) -> TokenSchema:
        user = await self.user_repository.get(email=email)
        if not user:
            raise ObjectNotFound(model_name="User", id_=email)

        if not self.verify_password(plain_password=password, hashed_password=user.password):
            raise InvalidCredentials("Invalid credentials provided")

        user = UserOutputSchema.model_validate(user)
        return self.generate_tokens_for_user(user=user)

    async def refresh_token(self, refresh_token: str) -> TokenSchema:
        verify = self.verify_token(token=refresh_token, token_type=TokenType.REFRESH)
        if not verify:
            raise InvalidCredentials("Invalid or expired refresh token")
        payload = self.decode_token(
            token=refresh_token, key=settings.token.SECRET_KEY, algorithms=[settings.token.ALGORITHM], options={}
        )
        email = payload.get("sub")
        user = await self.user_repository.get(email)
        if not user:
            raise ObjectNotFound("User", email)

        new_access_token = self.create_token(
            payload={"sub": user.email},
            token_type=TokenType.ACCESS,
            expire_minutes=settings.token.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        return TokenSchema(
            access_token=new_access_token, refresh_token=refresh_token, token_type=settings.token.TOKEN_TYPE
        )

    async def change_password(self, email: str, old_password: str, new_password: str) -> None:
        user = await self.user_repository.get(email)
        if not user:
            raise ObjectNotFound(model_name="User", id_=email)

        if not self.verify_password(plain_password=old_password, hashed_password=user.password):
            raise InvalidCredentials("Invalid credentials provided")

        hashed_new_password = self.hash_password(new_password)
        await self.user_repository.update_password(user=user, new_password=hashed_new_password)
