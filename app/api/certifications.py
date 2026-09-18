import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_graduate
from app.core.database import get_db
from app.models.certification import Certification
from app.models.graduate import Graduate
from app.schemas.certification import CertificationCreate, CertificationOut, CertificationUpdate

router = APIRouter(prefix="/certifications", tags=["Certifications"])


@router.get("", response_model=list[CertificationOut])
def list_certifications(graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    return db.query(Certification).filter(Certification.graduate_id == graduate.id).all()


@router.post("", response_model=CertificationOut, status_code=status.HTTP_201_CREATED)
def create_certification(payload: CertificationCreate, graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    record = Certification(graduate_id=graduate.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _get_owned_record(db: Session, graduate: Graduate, record_id: uuid.UUID) -> Certification:
    record = db.get(Certification, record_id)
    if not record or record.graduate_id != graduate.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certification not found")
    return record


@router.put("/{record_id}", response_model=CertificationOut)
def update_certification(record_id: uuid.UUID, payload: CertificationUpdate, graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    record = _get_owned_record(db, graduate, record_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certification(record_id: uuid.UUID, graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    record = _get_owned_record(db, graduate, record_id)
    db.delete(record)
    db.commit()
