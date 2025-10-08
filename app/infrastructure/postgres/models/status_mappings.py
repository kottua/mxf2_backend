from app.infrastructure.postgres.models.base import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class StatusMapping(Base):
    __tablename__ = "status_mappings"

    reo_id: Mapped[int] = mapped_column(Integer, ForeignKey("real_estate_objects.id"), nullable=False)
    dev_status: Mapped[str] = mapped_column(String, nullable=False)
    sys_status: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    real_estate_object: Mapped["RealEstateObject"] = relationship(back_populates="status_mappings")

    __table_args__ = {"sqlite_autoincrement": True, "extend_existing": True}
