from typing import List, Optional

from app.infrastructure.postgres.models.base import Base
from sqlalchemy import JSON, Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RealEstateObject(Base):
    __tablename__ = "real_estate_objects"

    name: Mapped[str] = mapped_column(String, nullable=False)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    curr: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="real_estate_objects")
    premises: Mapped[List["Premises"]] = relationship(back_populates="real_estate_object")
    pricing_config: Mapped[Optional["PricingConfig"]] = relationship(
        back_populates="real_estate_object", uselist=False
    )
    committed_prices: Mapped[List["CommittedPrices"]] = relationship(back_populates="real_estate_object")
    income_plans: Mapped[List["IncomePlan"]] = relationship(back_populates="real_estate_object")
    status_mappings: Mapped[List["StatusMapping"]] = relationship(back_populates="real_estate_object")

    __table_args__ = {"sqlite_autoincrement": True, "extend_existing": True}
