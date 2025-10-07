from typing import List

from app.infrastructure.postgres.models.base import Base
from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DistributionConfig(Base):
    __tablename__ = "distribution_configs"

    func_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    committed_prices: Mapped[List["CommittedPrices"]] = relationship(back_populates="distribution_config")

    __table_args__ = {"sqlite_autoincrement": True, "extend_existing": True}
