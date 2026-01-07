from typing import List

from app.infrastructure.postgres.models.base import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    real_estate_objects: Mapped[List["RealEstateObject"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    distribution_config: Mapped[List["DistributionConfig"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    api_key: Mapped["ApiKey"] = relationship(
        "ApiKey", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class ApiKey(Base):
    __tablename__ = "api_keys"

    key_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    key_value: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    user: Mapped["User"] = relationship(back_populates="api_key")

    __table_args__ = {"sqlite_autoincrement": True, "extend_existing": True}
