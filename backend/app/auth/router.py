from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from app.database import get_db
from app.config import get_settings
from app.auth.jwt import create_access_token
from app.auth.oauth import oauth
from app.auth.dependencies import get_current_user, bearer_scheme
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.common import APIResponse
from fastapi.security import HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()


@router.get("/google")
async def google_login(request: Request, role: str = "user"):
    """Redirect to Google OAuth consent screen."""
    # Store requested role in session for the callback to use
    request.session["requested_role"] = role
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Exchange authorization code for JWT."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        print("OAUTH ERROR:", str(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to authenticate with Google: {str(e)}",
        )

    userinfo = token.get("userinfo")
    if not userinfo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not retrieve user info from Google",
        )

    email = userinfo["email"]
    name = userinfo.get("name", "")
    avatar_url = userinfo.get("picture", "")
    requested_role = request.session.pop("requested_role", "user")

    from app.models.user import UserRole
    try:
        requested_user_role = UserRole(requested_role)
    except ValueError:
        requested_user_role = UserRole.user

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(email=email, name=name, avatar_url=avatar_url, role=requested_user_role)
        db.add(user)
        await db.flush()
    else:
        user.name = name or user.name
        user.avatar_url = avatar_url or user.avatar_url
        # Preserve existing role — don't overwrite on re-login

    access_token = create_access_token(
        {"user_id": str(user.id), "email": user.email, "role": user.role.value}
    )

    # Redirect to frontend with token
    frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
    return RedirectResponse(url=frontend_url)


@router.post("/logout", response_model=APIResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Invalidate the current JWT by storing it in the blacklist table."""
    token = credentials.credentials
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    blacklisted = TokenBlacklist(token=token, expires_at=expires_at)
    db.add(blacklisted)
    await db.flush()
    return APIResponse(message="Logged out successfully")
