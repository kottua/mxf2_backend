from typing import List

from app.core.utils.enums import ConfigStatus
from app.infrastructure.postgres.models.base import Base
from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DistributionConfig(Base):
    __tablename__ = "distribution_configs"

    func_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    config_status: Mapped[ConfigStatus] = mapped_column(
        Enum(ConfigStatus, name="configstatus_enum", create_type=True, native_enum=False),
        default=ConfigStatus.CUSTOM,
        nullable=False,
        server_default=ConfigStatus.CUSTOM,
    )

    # Relationships
    committed_prices: Mapped[List["CommittedPrices"]] = relationship(back_populates="distribution_config")
    user: Mapped["User"] = relationship(back_populates="distribution_config")

    __table_args__ = {"sqlite_autoincrement": True, "extend_existing": True}
