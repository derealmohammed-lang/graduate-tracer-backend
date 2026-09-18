import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.graduate import Graduate
from app.models.user import User, UserRole
from app.schemas.user import UserMeOut, UserMeUpdate

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def build_user_me(db: Session, user: User) -> UserMeOut:
    if user.role == UserRole.GRADUATE:
        graduate = db.query(Graduate).filter(Graduate.user_id == user.id).first()
        if graduate:
            return UserMeOut(
                id=user.id,
                email=user.email,
                phone=user.phone or graduate.phone,
                role=user.role,
                full_name=graduate.full_name,
                first_name=graduate.first_name,
                last_name=graduate.last_name,
                profile_photo=graduate.profile_photo or user.profile_photo,
            )

    return UserMeOut(
        id=user.id,
        email=user.email,
        phone=user.phone,
        role=user.role,
        full_name=user.full_name,
        profile_photo=user.profile_photo,
    )


def _ensure_unique_email(db: Session, email: str, user_id: uuid.UUID) -> None:
    existing = db.query(User).filter(User.email == email, User.id != user_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")


def update_user_me(db: Session, user: User, payload: UserMeUpdate) -> UserMeOut:
    data = payload.model_dump(exclude_unset=True)

    if "email" in data and data["email"]:
        _ensure_unique_email(db, data["email"], user.id)
        user.email = data["email"]

    if "phone" in data:
        user.phone = data["phone"] or None

    if user.role == UserRole.GRADUATE:
        graduate = db.query(Graduate).filter(Graduate.user_id == user.id).first()
        if graduate is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate profile not found")

        if "email" in data and data["email"]:
            graduate.email = data["email"]
        if "phone" in data:
            graduate.phone = data["phone"] or None
        if "first_name" in data and data["first_name"]:
            graduate.first_name = data["first_name"]
        if "last_name" in data and data["last_name"]:
            graduate.last_name = data["last_name"]
    else:
        if "full_name" in data:
            user.full_name = (data["full_name"] or "").strip() or None

    db.commit()
    db.refresh(user)
    return build_user_me(db, user)


async def save_profile_photo(db: Session, user: User, upload: UploadFile) -> UserMeOut:
    if upload.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload a JPEG, PNG, WebP, or GIF image")

    raw = await upload.read()
    max_bytes = settings.MAX_PROFILE_PHOTO_MB * 1024 * 1024
    if len(raw) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image is too large (max {settings.MAX_PROFILE_PHOTO_MB} MB)",
        )

    ext = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }[upload.content_type]

    upload_root = Path(settings.UPLOAD_DIR)
    user_dir = upload_root / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    filename = f"profile_{uuid.uuid4().hex}{ext}"
    file_path = user_dir / filename
    file_path.write_bytes(raw)

    photo_url = f"/uploads/{user.id}/{filename}"

    if user.role == UserRole.GRADUATE:
        graduate = db.query(Graduate).filter(Graduate.user_id == user.id).first()
        if graduate:
            graduate.profile_photo = photo_url
    user.profile_photo = photo_url

    db.commit()
    db.refresh(user)
    return build_user_me(db, user)
