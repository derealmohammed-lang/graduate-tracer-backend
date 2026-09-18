import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationBroadcastCreate(BaseModel):
    title: str
    message: str
    notification_type: str = "announcement"
    # Targeting: if all fields below are None, it goes to every graduate.
    target_program_id: uuid.UUID | None = None
    target_graduation_year: int | None = None
    target_employment_status: str | None = None


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    message: str
    notification_type: str
    created_at: datetime


class UserNotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    notification: NotificationOut
    is_read: bool
    read_at: datetime | None
