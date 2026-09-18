import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class EducationRecordBase(BaseModel):
    institution: str
    program: str
    level: str
    field_of_study: str | None = None
    start_date: date | None = None
    expected_completion: date | None = None
    completion_date: date | None = None
    country: str | None = None
    status: str = "Ongoing"


class EducationRecordCreate(EducationRecordBase):
    pass


class EducationRecordUpdate(BaseModel):
    institution: str | None = None
    program: str | None = None
    level: str | None = None
    field_of_study: str | None = None
    start_date: date | None = None
    expected_completion: date | None = None
    completion_date: date | None = None
    country: str | None = None
    status: str | None = None


class EducationRecordOut(EducationRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    graduate_id: uuid.UUID
