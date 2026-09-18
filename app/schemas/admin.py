import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import UserRole


class DepartmentCreate(BaseModel):
    name: str
    code: str
    description: str | None = None
    status: str = "Active"


class DepartmentUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    status: str | None = None


class DepartmentOut(DepartmentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class ProgramCreate(BaseModel):
    name: str
    code: str
    department_id: uuid.UUID
    description: str | None = None
    status: str = "Active"


class ProgramUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    department_id: uuid.UUID | None = None
    description: str | None = None
    status: str | None = None


class ProgramOut(ProgramCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID


class AdministratorCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.ADMINISTRATOR


class AdministratorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    full_name: str | None
    email: str
    role: UserRole
    is_active: bool
    last_login: datetime | None


class AdministratorStatusUpdate(BaseModel):
    is_active: bool


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID | None
    user_name: str | None = None
    action: str
    table_name: str
    record_id: str
    created_at: datetime


class GraduateSummaryOut(BaseModel):
    id: uuid.UUID
    full_name: str
    admission_number: str
    email: str | None
    program: str | None
    employment_status: str | None
    is_active: bool


class AdminDashboardStats(BaseModel):
    total_graduates: int
    total_active_surveys: int
    overall_response_rate: float
    employment_status_breakdown: dict[str, int]
