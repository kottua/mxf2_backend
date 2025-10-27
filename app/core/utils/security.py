from datetime import datetime, timedelta, timezone

import jwt
from app.core.exceptions import InvalidCredentials
from app.core.schemas.auth_schemas import TokenType
from app.settings import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthSecurity:

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_token(self, payload: dict, token_type: TokenType, expire_minutes: int) -> str:
        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
        to_encode.update({"exp": expire, "type": token_type})
        return jwt.encode(to_encode, settings.token.SECRET_KEY, algorithm=settings.token.ALGORITHM)

    def decode_token(self, token: str, key: str, options: dict, algorithms: list[str]) -> dict:
        try:
            payload = jwt.decode(jwt=token, key=key, algorithms=algorithms, options=options)
            return payload
        except jwt.ExpiredSignatureError:
            raise InvalidCredentials("Token has expired")
        except (jwt.InvalidTokenError, jwt.DecodeError):
            raise InvalidCredentials("Invalid token")

    def verify_token(self, token: str, token_type: TokenType) -> bool:
        try:
            payload = self.decode_token(
                token=token, key=settings.token.SECRET_KEY, algorithms=[settings.token.ALGORITHM], options={}
            )

            if payload.get("type") != token_type.value:
                raise InvalidCredentials("Invalid token type")
            return True

        except InvalidCredentials:
            return False
        except ValueError:
            return False
