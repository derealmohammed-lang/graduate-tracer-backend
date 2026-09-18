import secrets
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.academic import GraduationRecord
from app.models.graduate import Graduate
from app.models.password_reset import PasswordReset
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest


def register_graduate(db: Session, data: RegisterRequest) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ValueError("An account with this email already exists")

    user = User(
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=UserRole.GRADUATE,
    )
    db.add(user)
    db.flush()  # assign user.id without committing yet

    graduate = Graduate(
        user_id=user.id,
        admission_number=data.admission_number,
        first_name=data.first_name,
        middle_name=data.middle_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
    )
    db.add(graduate)
    db.flush()  # assign graduate.id for the graduation record below

    graduation_date = date.fromisoformat(data.graduation_date) if data.graduation_date else None
    db.add(
        GraduationRecord(
            graduate_id=graduate.id,
            program_id=data.program_id,
            graduation_year=data.graduation_year,
            graduation_date=graduation_date,
        )
    )

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    user.last_login = datetime.utcnow()
    db.commit()
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    access_token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    refresh_token = create_refresh_token(subject=str(user.id))
    return access_token, refresh_token


def create_password_reset_token(db: Session, email: str) -> str | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Deliberately don't reveal whether the email exists.
        return None

    token = secrets.token_urlsafe(32)
    reset = PasswordReset(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset)
    db.commit()
    # TODO: send this token via email (e.g. through an email service) instead
    # of returning it directly once real email delivery is wired up.
    return token


def reset_password(db: Session, token: str, new_password: str) -> bool:
    reset = db.query(PasswordReset).filter(PasswordReset.token == token, PasswordReset.used.is_(False)).first()
    if not reset or reset.expires_at < datetime.now(timezone.utc):
        return False

    user = db.get(User, reset.user_id)
    if not user:
        return False

    user.password_hash = hash_password(new_password)
    reset.used = True
    db.commit()
    return True
