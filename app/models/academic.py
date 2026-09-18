import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="Active", nullable=False)

    programs: Mapped[list["Program"]] = relationship(back_populates="department", cascade="all, delete-orphan")


class Program(Base):
    __tablename__ = "programs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="Active", nullable=False)

    department: Mapped["Department"] = relationship(back_populates="programs")
    graduation_records: Mapped[list["GraduationRecord"]] = relationship(back_populates="program")


class GraduationRecord(Base):
    __tablename__ = "graduation_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graduate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("graduates.id", ondelete="CASCADE"), nullable=False)
    program_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    graduation_year: Mapped[int] = mapped_column(nullable=False)
    graduation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    qualification: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    graduate: Mapped["Graduate"] = relationship(back_populates="graduation_records")
    program: Mapped["Program"] = relationship(back_populates="graduation_records")
