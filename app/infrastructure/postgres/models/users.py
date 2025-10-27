from typing import List

from app.infrastructure.postgres.models.base import Base
from sqlalchemy import String
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
