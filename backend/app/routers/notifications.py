import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.broker import Broker
from app.models.notification import Notification
from app.schemas.notification import NotificationOut
from app.schemas.common import APIResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=APIResponse[list[NotificationOut]])
async def list_notifications(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("broker")),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current broker."""
    broker_result = await db.execute(
        select(Broker).where(Broker.user_id == current_user.id)
    )
    broker = broker_result.scalar_one_or_none()
    if not broker:
        return APIResponse(data=[])

    stmt = select(Notification).where(Notification.broker_id == broker.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)  # noqa: E712
    stmt = stmt.order_by(Notification.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    notifications = list(result.scalars().all())
    return APIResponse(data=[NotificationOut.model_validate(n) for n in notifications])


@router.get("/unread-count", response_model=APIResponse[int])
async def unread_count(
    current_user: User = Depends(require_role("broker")),
    db: AsyncSession = Depends(get_db),
):
    """Get the count of unread notifications for the current broker."""
    broker_result = await db.execute(
        select(Broker).where(Broker.user_id == current_user.id)
    )
    broker = broker_result.scalar_one_or_none()
    if not broker:
        return APIResponse(data=0)

    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.broker_id == broker.id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    count = result.scalar() or 0
    return APIResponse(data=count)


@router.put("/{notification_id}/read", response_model=APIResponse[NotificationOut])
async def mark_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(require_role("broker")),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    broker_result = await db.execute(
        select(Broker).where(Broker.user_id == current_user.id)
    )
    broker = broker_result.scalar_one_or_none()
    if not broker:
        raise HTTPException(status_code=404, detail="Broker profile not found")

    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.broker_id == broker.id,
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    await db.flush()
    return APIResponse(
        data=NotificationOut.model_validate(notification),
        message="Notification marked as read",
    )
