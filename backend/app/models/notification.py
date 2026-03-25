import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class NotificationType(str, enum.Enum):
    new_assignment = "new_assignment"
    broker_request = "broker_request"
    listing_verified = "listing_verified"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True, index=True
    )
    broker_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brokers.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    listing_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("listings.id"), nullable=True
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType, name="notification_type"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    broker = relationship("Broker", foreign_keys=[broker_id], lazy="selectin")
    from_user = relationship("User", foreign_keys=[user_id], lazy="selectin")
