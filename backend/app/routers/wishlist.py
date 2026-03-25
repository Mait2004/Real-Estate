import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.wishlist import Wishlist
from app.models.listing import Listing
from app.schemas.wishlist import WishlistItemOut
from app.schemas.common import APIResponse

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.post("/{listing_id}", response_model=APIResponse[WishlistItemOut], status_code=201)
async def add_to_wishlist(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a listing to the current user's wishlist."""
    # Verify listing exists
    listing_result = await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.is_deleted == False)  # noqa: E712
    )
    listing_obj = listing_result.scalar_one_or_none()
    if not listing_obj:
        raise HTTPException(status_code=404, detail="Listing not found")

    # Check for duplicate
    existing = await db.execute(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.listing_id == listing_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already in wishlist")

    item = Wishlist(user_id=current_user.id, listing_id=listing_id)
    db.add(item)
    await db.flush()

    # Manually attach relationship to avoid MissingGreenlet on lazy load
    item.listing = listing_obj

    return APIResponse(
        data=WishlistItemOut.model_validate(item),
        message="Added to wishlist",
        status_code=201,
    )


@router.delete("/{listing_id}", response_model=APIResponse)
async def remove_from_wishlist(
    listing_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a listing from the current user's wishlist."""
    result = await db.execute(
        select(Wishlist).where(
            Wishlist.user_id == current_user.id,
            Wishlist.listing_id == listing_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not in wishlist")

    await db.delete(item)
    return APIResponse(message="Removed from wishlist")


@router.get("", response_model=APIResponse[list[WishlistItemOut]])
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all wishlisted listings for the current user."""
    result = await db.execute(
        select(Wishlist)
        .options(joinedload(Wishlist.listing))
        .where(Wishlist.user_id == current_user.id)
        .order_by(Wishlist.added_at.desc())
    )
    items = list(result.scalars().all())
    return APIResponse(data=[WishlistItemOut.model_validate(i) for i in items])
