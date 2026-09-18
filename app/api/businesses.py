import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_graduate
from app.core.database import get_db
from app.models.business import Business
from app.models.graduate import Graduate
from app.schemas.business import BusinessCreate, BusinessOut, BusinessUpdate

router = APIRouter(prefix="/businesses", tags=["Businesses"])


@router.get("", response_model=list[BusinessOut])
def list_businesses(graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    return db.query(Business).filter(Business.graduate_id == graduate.id).all()


@router.post("", response_model=BusinessOut, status_code=status.HTTP_201_CREATED)
def create_business(payload: BusinessCreate, graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    record = Business(graduate_id=graduate.id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def _get_owned_record(db: Session, graduate: Graduate, record_id: uuid.UUID) -> Business:
    record = db.get(Business, record_id)
    if not record or record.graduate_id != graduate.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    return record


@router.put("/{record_id}", response_model=BusinessOut)
def update_business(record_id: uuid.UUID, payload: BusinessUpdate, graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    record = _get_owned_record(db, graduate, record_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(record_id: uuid.UUID, graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    record = _get_owned_record(db, graduate, record_id)
    db.delete(record)
    db.commit()
