import uuid
import json
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import WKTElement
from geoalchemy2.functions import ST_Contains, ST_SetSRID, ST_MakePoint
from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.listing import Listing
from app.models.broker import Broker, BrokerAssignment, AssignmentStatus
from app.models.notification import Notification, NotificationType
from app.schemas.broker import BrokerRegister, BrokerOut, BrokerAssignmentOut
from app.schemas.listing import ListingOut
from app.schemas.common import APIResponse

router = APIRouter(prefix="/brokers", tags=["Brokers"])


def _geojson_to_wkt(geojson: dict) -> str:
    """Convert a GeoJSON Polygon to WKT string."""
    coords = geojson["coordinates"][0]
    ring = ", ".join(f"{c[0]} {c[1]}" for c in coords)
    return f"POLYGON(({ring}))"


@router.post("/register", response_model=APIResponse[BrokerOut], status_code=201)
async def register_broker(
    payload: BrokerRegister,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register as a broker with a locality polygon."""
    # Check if already registered
    existing = await db.execute(select(Broker).where(Broker.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already registered as a broker")

    wkt = _geojson_to_wkt(payload.locality_polygon)
    broker = Broker(
        user_id=current_user.id,
        locality_name=payload.locality_name,
        locality_polygon=WKTElement(wkt, srid=4326),
    )
    db.add(broker)

    # Update user role
    current_user.role = "broker"
    await db.flush()

    return APIResponse(
        data=BrokerOut.model_validate(broker),
        message="Broker registration submitted",
        status_code=201,
    )


@router.get("", response_model=APIResponse[list[BrokerOut]])
async def list_brokers(
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """List all brokers (admin only)."""
    result = await db.execute(select(Broker).order_by(Broker.created_at.desc()))
    brokers = list(result.scalars().all())
    return APIResponse(data=[BrokerOut.model_validate(b) for b in brokers])


@router.get("/{broker_id}/contact", response_model=APIResponse[dict])
async def get_broker_contact(
    broker_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get public contact information for a broker."""
    result = await db.execute(select(Broker, User).join(User, Broker.user_id == User.id).where(Broker.id == broker_id))
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Broker not found")
    broker, user = row
    
    return APIResponse(data={
        "name": user.name,
        "email": user.email,
        "rating": broker.rating,
        "locality": broker.locality_name
    })


@router.put("/{broker_id}/verify", response_model=APIResponse[BrokerOut])
async def verify_broker(
    broker_id: uuid.UUID,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Admin verifies a broker."""
    result = await db.execute(select(Broker).where(Broker.id == broker_id))
    broker = result.scalar_one_or_none()
    if not broker:
        raise HTTPException(status_code=404, detail="Broker not found")
    broker.verified = True
    await db.flush()
    return APIResponse(data=BrokerOut.model_validate(broker), message="Broker verified")


@router.get("/my-listings", response_model=APIResponse[list[ListingOut]])
async def my_listings(
    current_user: User = Depends(require_role("broker")),
    db: AsyncSession = Depends(get_db),
):
    """Broker sees all listings assigned to them."""
    broker_result = await db.execute(
        select(Broker).where(Broker.user_id == current_user.id)
    )
    broker = broker_result.scalar_one_or_none()
    if not broker:
        return APIResponse(data=[])

    result = await db.execute(
        select(Listing)
        .where(Listing.broker_id == broker.id, Listing.is_deleted == False)  # noqa: E712
        .order_by(Listing.created_at.desc())
    )
    listings = list(result.scalars().all())
    return APIResponse(data=[ListingOut.model_validate(l) for l in listings])


@router.put("/{broker_id}/listing/{listing_id}/verify", response_model=APIResponse[ListingOut])
async def verify_listing(
    broker_id: uuid.UUID,
    listing_id: uuid.UUID,
    current_user: User = Depends(require_role("broker")),
    db: AsyncSession = Depends(get_db),
):
    """Broker marks a listing as verified."""
    broker_result = await db.execute(
        select(Broker).where(Broker.id == broker_id, Broker.user_id == current_user.id)
    )
    broker = broker_result.scalar_one_or_none()
    if not broker:
        raise HTTPException(status_code=403, detail="Not your broker profile")

    result = await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.broker_id == broker.id)
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or not assigned to you")

    listing.status = "verified"
    await db.flush()
    return APIResponse(data=ListingOut.model_validate(listing), message="Listing verified")


@router.post(
    "/{listing_id}/change-broker",
    response_model=APIResponse[BrokerAssignmentOut],
    status_code=201,
    tags=["Listings"],
)
async def change_broker(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """User requests a broker swap; pick another random broker from the same locality."""
    result = await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.is_deleted == False)  # noqa: E712
    )
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorised")

    current_broker_id = listing.broker_id

    # Find other brokers whose polygon contains this listing
    point = ST_SetSRID(ST_MakePoint(listing.lng, listing.lat), 4326)
    stmt = select(Broker).where(
        Broker.verified == True,  # noqa: E712
        ST_Contains(Broker.locality_polygon, point),
    )
    if current_broker_id:
        stmt = stmt.where(Broker.id != current_broker_id)

    broker_result = await db.execute(stmt)
    candidates = list(broker_result.scalars().all())
    if not candidates:
        raise HTTPException(status_code=404, detail="No other brokers available in this locality")

    new_broker = random.choice(candidates)

    # Mark old assignment as swapped
    if current_broker_id:
        old_assignment = await db.execute(
            select(BrokerAssignment).where(
                BrokerAssignment.listing_id == listing_id,
                BrokerAssignment.broker_id == current_broker_id,
                BrokerAssignment.status == AssignmentStatus.active,
            )
        )
        old = old_assignment.scalar_one_or_none()
        if old:
            old.status = AssignmentStatus.swapped

    listing.broker_id = new_broker.id
    new_broker.total_assignments += 1

    new_assignment = BrokerAssignment(
        listing_id=listing_id,
        broker_id=new_broker.id,
    )
    db.add(new_assignment)

    # Notify the new broker
    notification = Notification(
        broker_id=new_broker.id,
        user_id=current_user.id,
        listing_id=listing_id,
        type=NotificationType.broker_request,
        message=f"You have been assigned to listing \"{listing.title}\" after a broker swap request.",
    )
    db.add(notification)
    await db.flush()

    return APIResponse(
        data=BrokerAssignmentOut.model_validate(new_assignment),
        message="Broker swapped successfully",
        status_code=201,
    )
