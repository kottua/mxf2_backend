from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenSettings(BaseSettings):
    SECRET_KEY: str = Field(..., alias="JWT_SECRET_KEY")
    ALGORITHM: str = Field(..., alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, alias="JWT_REFRESH_TOKEN_EXPIRE_MINUTES")
    TOKEN_TYPE: str = Field(..., alias="JWT_TOKEN_TYPE")

    model_config = SettingsConfigDict(env_file=".env", env_prefix="JWT_", extra="ignore")


class DatabaseSettings(BaseSettings):
    POSTGRES_DRIVER: str = Field(default="postgresql+asyncpg", alias="POSTGRES_DRIVER")
    POSTGRES_USER: str = Field(..., alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., alias="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(..., alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(..., alias="POSTGRES_DB")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.POSTGRES_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class Settings(BaseSettings):
    HOST: str = Field(default="localhost", alias="HOST")
    PORT: int = Field(default=8000, alias="PORT")

    database: DatabaseSettings = DatabaseSettings()
    token: TokenSettings = TokenSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
