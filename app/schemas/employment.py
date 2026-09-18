import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.employment import EmploymentStatus


class EmploymentRecordBase(BaseModel):
    employment_status: EmploymentStatus
    employer_name: str | None = None
    job_title: str | None = None
    industry: str | None = None
    employment_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    salary_range: str | None = None
    location: str | None = None
    country: str | None = None
    related_to_degree: bool | None = None
    how_obtained: str | None = None
    is_current: bool = True


class EmploymentRecordCreate(EmploymentRecordBase):
    pass


class EmploymentRecordUpdate(BaseModel):
    employment_status: EmploymentStatus | None = None
    employer_name: str | None = None
    job_title: str | None = None
    industry: str | None = None
    employment_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    salary_range: str | None = None
    location: str | None = None
    country: str | None = None
    related_to_degree: bool | None = None
    how_obtained: str | None = None
    is_current: bool | None = None


class EmploymentRecordOut(EmploymentRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    graduate_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
