import uuid
from datetime import datetime
from pydantic import BaseModel
from app.schemas.listing import ListingOut


class WishlistItemOut(BaseModel):
    id: uuid.UUID
    listing_id: uuid.UUID
    added_at: datetime
    listing: ListingOut | None = None

    model_config = {"from_attributes": True}
