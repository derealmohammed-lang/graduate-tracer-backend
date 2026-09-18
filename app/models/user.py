import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserRole(str, enum.Enum):
    GRADUATE = "graduate"
    ADMINISTRATOR = "administrator"
    SUPER_ADMINISTRATOR = "super_administrator"


class User(Base):
    """Authentication identity. A Graduate profile hangs off a user with
    role=GRADUATE via a 1:1 relationship; administrators typically don't
    have a graduate profile at all.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.GRADUATE)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Full name fields are useful for administrator accounts, which have no
    # separate `graduates` row of their own.
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_photo: Mapped[str | None] = mapped_column(String(500), nullable=True)

    graduate: Mapped["Graduate | None"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
