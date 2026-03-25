import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Float, Integer, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class UserRole(str, enum.Enum):
    user = "user"
    broker = "broker"
    admin = "admin"


class PropertyType(str, enum.Enum):
    flat = "flat"
    villa = "villa"
    land = "land"
    bungalow = "bungalow"


class Purpose(str, enum.Enum):
    rent = "rent"
    buy = "buy"
    both = "both"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.user, nullable=False
    )
    onboarding_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    # Preferences / onboarding
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    budget_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferred_type: Mapped[PropertyType | None] = mapped_column(
        Enum(PropertyType, name="property_type"), nullable=True
    )
    purpose: Mapped[Purpose | None] = mapped_column(
        Enum(Purpose, name="purpose"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
