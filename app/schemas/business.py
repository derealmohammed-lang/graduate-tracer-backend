import uuid

from pydantic import BaseModel, ConfigDict


class BusinessBase(BaseModel):
    business_name: str
    business_type: str | None = None
    industry: str | None = None
    description: str | None = None
    location: str | None = None
    year_started: int | None = None
    employee_count: int | None = None
    status: str = "Active"
    website: str | None = None
    contact: str | None = None


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BaseModel):
    business_name: str | None = None
    business_type: str | None = None
    industry: str | None = None
    description: str | None = None
    location: str | None = None
    year_started: int | None = None
    employee_count: int | None = None
    status: str | None = None
    website: str | None = None
    contact: str | None = None


class BusinessOut(BusinessBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    graduate_id: uuid.UUID
