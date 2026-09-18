import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class GraduateBase(BaseModel):
    first_name: str
    middle_name: str | None = None
    last_name: str
    gender: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    county: str | None = None
    country: str | None = None


class GraduateUpdate(BaseModel):
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    county: str | None = None
    country: str | None = None
    profile_photo: str | None = None


class GraduateOut(GraduateBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    admission_number: str
    profile_photo: str | None = None
    created_at: datetime
    updated_at: datetime


class GraduateProfileOut(GraduateOut):
    """Enriched profile combining the graduate's own record with the fields
    the app's dashboard/profile screens need: their program & graduation
    year (from graduation_records/programs) and current employment status
    (from the current employment_records row), computed by the API layer
    rather than stored directly on Graduate.
    """

    program: str | None = None
    department: str | None = None
    graduation_year: int | None = None
    employment_status: str | None = None
    current_position: str | None = None
    profile_completion: float = 0.0
