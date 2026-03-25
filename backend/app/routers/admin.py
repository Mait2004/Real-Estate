import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import require_role
from app.models.user import User
from app.models.listing import Listing, ListingStatus
from app.models.broker import Broker, BrokerAssignment, AssignmentStatus
from app.models.notification import Notification, NotificationType
from app.schemas.user import UserOut
from app.schemas.listing import ListingOut
from app.schemas.broker import BrokerOut
from app.schemas.common import APIResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=APIResponse[list[UserOut]])
async def list_users(
    role: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """List all users with optional role filter."""
    stmt = select(User).order_by(User.created_at.desc())
    if role:
        stmt = stmt.where(User.role == role)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    users = list(result.scalars().all())
    return APIResponse(data=[UserOut.model_validate(u) for u in users])


@router.get("/listings", response_model=APIResponse[list[ListingOut]])
async def list_all_listings(
    status: ListingStatus | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """List all listings including pending (admin only)."""
    stmt = select(Listing).where(Listing.is_deleted == False).order_by(  # noqa: E712
        Listing.created_at.desc()
    )
    if status:
        stmt = stmt.where(Listing.status == status)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    listings = list(result.scalars().all())
    return APIResponse(data=[ListingOut.model_validate(l) for l in listings])


@router.put("/listings/{listing_id}/status", response_model=APIResponse[ListingOut])
async def set_listing_status(
    listing_id: uuid.UUID,
    status: ListingStatus,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Set listing status to active/suspended etc."""
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.status = status
    await db.flush()
    return APIResponse(
        data=ListingOut.model_validate(listing), message=f"Status set to {status.value}"
    )


@router.get("/brokers", response_model=APIResponse[list[BrokerOut]])
async def list_broker_applications(
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """List all broker applications with user details."""
    result = await db.execute(
        select(Broker, User.name, User.email)
        .join(User, Broker.user_id == User.id)
        .order_by(Broker.created_at.desc())
    )
    
    brokers = []
    for broker, name, email in result.all():
        broker.user_name = name
        broker.user_email = email
        brokers.append(broker)
        
    return APIResponse(data=[BrokerOut.model_validate(b) for b in brokers])


@router.put("/listings/{listing_id}/broker/{broker_id}", response_model=APIResponse[ListingOut])
async def reassign_listing_broker(
    listing_id: uuid.UUID,
    broker_id: uuid.UUID,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Admin reassigns a listing to a specific broker."""
    # 1. Verify listing exists
    listing_result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = listing_result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # 2. Verify broker exists
    broker_result = await db.execute(select(Broker).where(Broker.id == broker_id))
    new_broker = broker_result.scalar_one_or_none()
    if not new_broker:
        raise HTTPException(status_code=404, detail="Broker not found")

    # 3. Swap out old assignment if any
    old_broker_id = listing.broker_id
    if old_broker_id:
        old_assignment = await db.execute(
            select(BrokerAssignment).where(
                BrokerAssignment.listing_id == listing_id,
                BrokerAssignment.broker_id == old_broker_id,
                BrokerAssignment.status == AssignmentStatus.active,
            )
        )
        old = old_assignment.scalar_one_or_none()
        if old:
            old.status = AssignmentStatus.swapped

    # 4. Assign new broker
    listing.broker_id = new_broker.id
    new_broker.total_assignments += 1

    new_assignment = BrokerAssignment(
        listing_id=listing.id,
        broker_id=new_broker.id,
        status=AssignmentStatus.active
    )
    db.add(new_assignment)

    # 5. Notify new broker
    notification = Notification(
        user_id=listing.user_id,
        broker_id=new_broker.id,
        listing_id=listing.id,
        type=NotificationType.new_assignment,
        message=f"Admin assigned you to listing \"{listing.title}\"."
    )
    db.add(notification)
    
    await db.flush()

    return APIResponse(
        data=ListingOut.model_validate(listing), 
        message="Broker assigned successfully"
    )


@router.delete("/users/{user_id}", response_model=APIResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    _: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate (soft-delete) a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.flush()
    return APIResponse(message="User deactivated")
