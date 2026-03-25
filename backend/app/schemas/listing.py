import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.listing import ListingType, ListingPurpose, ListingStatus


class ListingCreate(BaseModel):
    type: ListingType
    purpose: ListingPurpose
    title: str
    description: str | None = None
    price: int
    area_sqft: int
    bedrooms: int | None = None
    city: str
    address: str | None = None
    lat: float
    lng: float


class ListingUpdate(BaseModel):
    type: ListingType | None = None
    purpose: ListingPurpose | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    area_sqft: int | None = None
    bedrooms: int | None = None
    city: str | None = None
    address: str | None = None
    lat: float | None = None
    lng: float | None = None


class ListingOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    broker_id: uuid.UUID | None = None
    type: ListingType
    purpose: ListingPurpose
    title: str
    description: str | None = None
    price: int
    area_sqft: int
    bedrooms: int | None = None
    city: str
    address: str | None = None
    lat: float
    lng: float
    images: list[str] | None = None
    status: ListingStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class ListingFilter(BaseModel):
    purpose: ListingPurpose | None = None
    type: ListingType | None = None
    city: str | None = None
    price_min: int | None = None
    price_max: int | None = None
    area_min: int | None = None
    area_max: int | None = None
    page: int = 1
    page_size: int = 20
