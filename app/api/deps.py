import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.graduate import Graduate
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    if not token:
        raise credentials_error

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_error

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_error

    user = db.get(User, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_error

    return user


def get_current_graduate(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Graduate:
    if user.role != UserRole.GRADUATE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Graduate account required")

    graduate = db.query(Graduate).filter(Graduate.user_id == user.id).first()
    if graduate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate profile not found")

    return graduate


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in (UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator privileges required")
    return user


def require_super_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.SUPER_ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super administrator privileges required")
    return user
