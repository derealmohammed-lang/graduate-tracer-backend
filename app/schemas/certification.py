import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class CertificationBase(BaseModel):
    name: str
    issuing_organization: str
    certificate_number: str | None = None
    date_obtained: date | None = None
    expiry_date: date | None = None


class CertificationCreate(CertificationBase):
    attachment_url: str | None = None


class CertificationUpdate(BaseModel):
    name: str | None = None
    issuing_organization: str | None = None
    certificate_number: str | None = None
    date_obtained: date | None = None
    expiry_date: date | None = None
    attachment_url: str | None = None


class CertificationOut(CertificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    graduate_id: uuid.UUID
    attachment_url: str | None = None
