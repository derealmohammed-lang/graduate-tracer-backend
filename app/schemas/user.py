import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserMeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    phone: str | None = None
    role: UserRole
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile_photo: str | None = None


class UserMeUpdate(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    full_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)
