import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.notification import Notification, UserNotification
from app.models.user import User
from app.schemas.notification import NotificationBroadcastCreate, NotificationOut, UserNotificationOut
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[UserNotificationOut])
def list_my_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(UserNotification)
        .join(Notification)
        .filter(UserNotification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.put("/{user_notification_id}/read", response_model=UserNotificationOut)
def mark_as_read(user_notification_id: uuid.UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = db.get(UserNotification, user_notification_id)
    if not entry or entry.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    entry.is_read = True
    entry.read_at = datetime.utcnow()
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/broadcast", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
def broadcast(payload: NotificationBroadcastCreate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    return notification_service.broadcast_notification(db, payload, created_by=admin.id)
