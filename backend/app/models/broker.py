import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Float, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.models.base import Base


class Broker(Base):
    __tablename__ = "brokers"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    locality_name: Mapped[str] = mapped_column(String(255), nullable=False)
    locality_polygon = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=False
    )
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    total_assignments: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", foreign_keys=[user_id], lazy="selectin")


class AssignmentStatus(str, enum.Enum):
    active = "active"
    swapped = "swapped"
    completed = "completed"


class BrokerAssignment(Base):
    __tablename__ = "broker_assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    listing_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("listings.id"), nullable=False, index=True
    )
    broker_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brokers.id"), nullable=False, index=True
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus, name="assignment_status"),
        default=AssignmentStatus.active,
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    listing = relationship("Listing", foreign_keys=[listing_id], lazy="selectin")
    broker = relationship("Broker", foreign_keys=[broker_id], lazy="selectin")
