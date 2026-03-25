import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    id: uuid.UUID
    broker_id: uuid.UUID
    user_id: uuid.UUID | None = None
    listing_id: uuid.UUID | None = None
    type: NotificationType
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
