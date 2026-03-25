import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.listing import Listing
from app.models.wishlist import Wishlist
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.listing import ListingOut
from app.schemas.common import APIResponse
from app.config import get_settings

router = APIRouter(prefix="/chat", tags=["Chatbot"])
settings = get_settings()

genai.configure(api_key=settings.GEMINI_API_KEY)


@router.post("", response_model=APIResponse[ChatResponse])
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Context-aware property chatbot powered by Gemini 1.5 Flash."""
    # Fetch user's wishlist
    wishlist_result = await db.execute(
        select(Wishlist).where(Wishlist.user_id == current_user.id)
    )
    wishlist_items = list(wishlist_result.scalars().all())
    wishlist_listing_ids = [str(w.listing_id) for w in wishlist_items]

    # Fetch matching listings
    stmt = select(Listing).where(Listing.is_deleted == False)  # noqa: E712
    if current_user.preferred_type:
        stmt = stmt.where(Listing.type == current_user.preferred_type)
    if current_user.purpose and current_user.purpose.value != "both":
        stmt = stmt.where(Listing.purpose == current_user.purpose)
    if current_user.budget_min:
        stmt = stmt.where(Listing.price >= current_user.budget_min)
    if current_user.budget_max:
        stmt = stmt.where(Listing.price <= current_user.budget_max)
    stmt = stmt.order_by(Listing.created_at.desc()).limit(10)

    listings_result = await db.execute(stmt)
    listings = list(listings_result.scalars().all())
    listings_json = json.dumps(
        [ListingOut.model_validate(l).model_dump(mode="json") for l in listings],
        indent=2,
    )

    # Build wishlist summary
    if wishlist_listing_ids:
        wl_result = await db.execute(
            select(Listing).where(Listing.id.in_(wishlist_listing_ids))
        )
        wl_listings = list(wl_result.scalars().all())
        wishlist_summary = ", ".join(
            f"{l.title} ({l.city}, ₹{l.price})" for l in wl_listings
        )
    else:
        wishlist_summary = "No items in wishlist"

    system_prompt = (
        f"You are a helpful property assistant. "
        f"The user's location is {current_user.location_name or 'not set'}. "
        f"Their budget is ₹{current_user.budget_min or 'N/A'} to ₹{current_user.budget_max or 'N/A'}. "
        f"Their preferred property type is {current_user.preferred_type.value if current_user.preferred_type else 'any'}. "
        f"Their purpose is {current_user.purpose.value if current_user.purpose else 'not set'}. "
        f"Their wishlist contains: {wishlist_summary}. "
        f"Here are matching listings:\n{listings_json}\n\n"
        f"Answer their property questions and give personalised recommendations."
    )

    # Build conversation for Gemini
    model = genai.GenerativeModel("gemini-2.5-flash")

    history = []
    for msg in payload.conversation_history:
        history.append({"role": msg.role, "parts": [msg.content]})

    chat_session = model.start_chat(history=history)

    # Prepend system context to the user's message
    full_message = f"[System Context: {system_prompt}]\n\nUser question: {payload.message}"

    try:
        response = chat_session.send_message(full_message)
        reply = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

    return APIResponse(data=ChatResponse(reply=reply))
