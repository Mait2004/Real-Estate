import uuid
import random
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_Contains, ST_SetSRID, ST_MakePoint
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.listing import Listing, ListingStatus, ListingType, ListingPurpose
from app.models.broker import Broker, BrokerAssignment, AssignmentStatus
from app.models.notification import Notification, NotificationType
from app.schemas.listing import ListingCreate, ListingUpdate, ListingOut
from app.schemas.common import APIResponse
from app.config import get_settings
import cloudinary
import cloudinary.uploader

router = APIRouter(prefix="/listings", tags=["Listings"])
settings = get_settings()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


async def _auto_assign_broker(
    db: AsyncSession, listing: Listing
) -> Broker | None:
    """Find a verified broker whose polygon contains the listing point and assign randomly."""
    point = ST_SetSRID(ST_MakePoint(listing.lng, listing.lat), 4326)
    stmt = select(Broker).where(
        Broker.verified == True,  # noqa: E712
        ST_Contains(Broker.locality_polygon, point),
    )
    result = await db.execute(stmt)
    brokers = list(result.scalars().all())

    if not brokers:
        return None

    chosen = random.choice(brokers)
    listing.broker_id = chosen.id
    chosen.total_assignments += 1

    assignment = BrokerAssignment(
        listing_id=listing.id,
        broker_id=chosen.id,
    )
    db.add(assignment)
    return chosen


@router.post("", response_model=APIResponse[ListingOut], status_code=201)
async def create_listing(
    payload: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new listing and auto-assign a broker based on geolocation."""
    listing = Listing(**payload.model_dump(), user_id=current_user.id)
    db.add(listing)
    await db.flush()

    assigned_broker = await _auto_assign_broker(db, listing)
    if assigned_broker:
        notification = Notification(
            broker_id=assigned_broker.id,
            user_id=current_user.id,
            listing_id=listing.id,
            type=NotificationType.new_assignment,
            message=f"New listing \"{listing.title}\" in {listing.city} has been assigned to you.",
        )
        db.add(notification)
    await db.flush()

    return APIResponse(
        data=ListingOut.model_validate(listing),
        message="Listing created",
        status_code=201,
    )


@router.get("", response_model=APIResponse[list[ListingOut]])
async def list_listings(
    purpose: ListingPurpose | None = None,
    type: ListingType | None = None,
    city: str | None = None,
    price_min: int | None = None,
    price_max: int | None = None,
    area_min: int | None = None,
    area_max: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Paginated listing search with filters."""
    stmt = select(Listing).where(Listing.is_deleted == False)  # noqa: E712

    if purpose:
        stmt = stmt.where(Listing.purpose == purpose)
    if type:
        stmt = stmt.where(Listing.type == type)
    if city:
        stmt = stmt.where(Listing.city.ilike(f"%{city}%"))
    if price_min is not None:
        stmt = stmt.where(Listing.price >= price_min)
    if price_max is not None:
        stmt = stmt.where(Listing.price <= price_max)
    if area_min is not None:
        stmt = stmt.where(Listing.area_sqft >= area_min)
    if area_max is not None:
        stmt = stmt.where(Listing.area_sqft <= area_max)

    stmt = stmt.order_by(Listing.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    listings = list(result.scalars().all())
    return APIResponse(data=[ListingOut.model_validate(l) for l in listings])


@router.get("/{listing_id}", response_model=APIResponse[ListingOut])
async def get_listing(
    listing_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single listing by ID."""
    result = await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.is_deleted == False)  # noqa: E712
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return APIResponse(data=ListingOut.model_validate(listing))


@router.put("/{listing_id}", response_model=APIResponse[ListingOut])
async def update_listing(
    listing_id: uuid.UUID,
    payload: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a listing (owner, assigned broker, or admin only)."""
    result = await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.is_deleted == False)  # noqa: E712
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Permission check
    is_owner = listing.user_id == current_user.id
    is_admin = current_user.role.value == "admin"
    # Check if current user is the assigned broker
    is_broker = False
    if current_user.role.value == "broker":
        broker_result = await db.execute(
            select(Broker).where(Broker.user_id == current_user.id)
        )
        broker = broker_result.scalar_one_or_none()
        if broker and listing.broker_id == broker.id:
            is_broker = True

    if not (is_owner or is_admin or is_broker):
        raise HTTPException(status_code=403, detail="Not authorised to update this listing")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    await db.flush()

    return APIResponse(data=ListingOut.model_validate(listing), message="Listing updated")


@router.delete("/{listing_id}", response_model=APIResponse)
async def delete_listing(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a listing."""
    result = await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.is_deleted == False)  # noqa: E712
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorised")

    listing.is_deleted = True
    return APIResponse(message="Listing deleted")


@router.post("/{listing_id}/images", response_model=APIResponse[ListingOut])
async def upload_images(
    listing_id: uuid.UUID,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload images to Cloudinary and store URLs on the listing."""
    result = await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.is_deleted == False)  # noqa: E712
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not authorised")

    uploaded_urls: list[str] = []
    for file in files:
        upload_result = cloudinary.uploader.upload(
            file.file,
            folder=f"realestate/listings/{listing_id}",
        )
        uploaded_urls.append(upload_result["secure_url"])

    existing = listing.images or []
    listing.images = existing + uploaded_urls
    await db.flush()

    return APIResponse(
        data=ListingOut.model_validate(listing), message="Images uploaded"
    )
