import uuid

from sqlalchemy.orm import Session

from app.models.employment import EmploymentRecord
from app.models.graduate import Graduate
from app.models.graduate import Graduate as GraduateModel
from app.models.notification import Notification, UserNotification
from app.schemas.notification import NotificationBroadcastCreate


def broadcast_notification(db: Session, data: NotificationBroadcastCreate, created_by: uuid.UUID) -> Notification:
    notification = Notification(
        title=data.title,
        message=data.message,
        notification_type=data.notification_type,
        created_by=created_by,
    )
    db.add(notification)
    db.flush()

    query = db.query(GraduateModel)

    if data.target_graduation_year is not None:
        # Graduation year currently lives on graduation_records; a simple
        # direct-field filter is left as a TODO until that join is needed
        # for real targeting. For now this filter is a no-op placeholder.
        pass

    if data.target_employment_status is not None:
        query = (
            query.join(EmploymentRecord, EmploymentRecord.graduate_id == Graduate.id)
            .filter(EmploymentRecord.employment_status == data.target_employment_status, EmploymentRecord.is_current.is_(True))
        )

    graduates = query.all()

    for grad in graduates:
        db.add(UserNotification(notification_id=notification.id, user_id=grad.user_id))

    db.commit()
    db.refresh(notification)
    return notification
