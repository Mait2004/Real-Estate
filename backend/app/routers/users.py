from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate, OnboardingRequest
from app.schemas.common import APIResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=APIResponse[UserOut])
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the current user's profile and onboarding status."""
    return APIResponse(data=UserOut.model_validate(current_user))


@router.put("/me", response_model=APIResponse[UserOut])
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    return APIResponse(data=UserOut.model_validate(current_user), message="Profile updated")


@router.post("/onboarding", response_model=APIResponse[UserOut])
async def onboarding(
    payload: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save onboarding answers and mark onboarding as complete."""
    for field, value in payload.model_dump().items():
        setattr(current_user, field, value)
    current_user.onboarding_complete = True
    await db.flush()
    return APIResponse(
        data=UserOut.model_validate(current_user),
        message="Onboarding completed",
    )
