import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, PropertyType, Purpose


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    name: str | None = None
    avatar_url: str | None = None
    role: UserRole
    onboarding_complete: bool
    location_name: str | None = None
    lat: float | None = None
    lng: float | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    preferred_type: PropertyType | None = None
    purpose: Purpose | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    location_name: str | None = None
    lat: float | None = None
    lng: float | None = None
    budget_min: int | None = None
    budget_max: int | None = None
    preferred_type: PropertyType | None = None
    purpose: Purpose | None = None


class OnboardingRequest(BaseModel):
    location_name: str
    lat: float
    lng: float
    budget_min: int
    budget_max: int
    preferred_type: PropertyType
    purpose: Purpose
