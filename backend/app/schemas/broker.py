import uuid
from datetime import datetime
from pydantic import BaseModel


class BrokerRegister(BaseModel):
    locality_name: str
    locality_polygon: dict  # GeoJSON


class BrokerOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str | None = None
    user_email: str | None = None
    locality_name: str
    verified: bool
    rating: float
    total_assignments: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BrokerAssignmentOut(BaseModel):
    id: uuid.UUID
    listing_id: uuid.UUID
    broker_id: uuid.UUID
    status: str
    assigned_at: datetime

    model_config = {"from_attributes": True}
