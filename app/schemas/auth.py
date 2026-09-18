import uuid

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str
    password: str = Field(min_length=6)
    first_name: str
    last_name: str
    middle_name: str | None = None
    admission_number: str
    program_id: uuid.UUID
    graduation_year: int
    graduation_date: str | None = None  # ISO date string, optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: UserRole


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str
