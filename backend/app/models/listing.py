import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import (
    String, Integer, Float, Enum, DateTime, ForeignKey, ARRAY, Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class ListingType(str, enum.Enum):
    flat = "flat"
    villa = "villa"
    land = "land"
    bungalow = "bungalow"


class ListingPurpose(str, enum.Enum):
    rent = "rent"
    buy = "buy"


class ListingStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    active = "active"
    sold = "sold"
    rented = "rented"
    suspended = "suspended"


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    broker_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("brokers.id"), nullable=True, index=True
    )
    type: Mapped[ListingType] = mapped_column(
        Enum(ListingType, name="listing_type"), nullable=False
    )
    purpose: Mapped[ListingPurpose] = mapped_column(
        Enum(ListingPurpose, name="listing_purpose"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    area_sqft: Mapped[int] = mapped_column(Integer, nullable=False)
    bedrooms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    city: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    images: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status"), default=ListingStatus.pending
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    owner = relationship("User", foreign_keys=[user_id], lazy="selectin")
