from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.academic import Department, Program
from app.schemas.admin import DepartmentOut, ProgramOut

router = APIRouter(tags=["Public"])


@router.get("/programs", response_model=list[ProgramOut])
def list_programs_public(db: Session = Depends(get_db)):
    """Unauthenticated program list, used by the registration form so a new
    graduate can pick their program before they have an account. Admins use
    the richer `/admin/programs` (same shape today, but kept separate so
    admin-only fields can be added there later without affecting this
    public endpoint).
    """
    return db.query(Program).filter(Program.status == "Active").all()


@router.get("/departments", response_model=list[DepartmentOut])
def list_departments_public(db: Session = Depends(get_db)):
    return db.query(Department).filter(Department.status == "Active").all()
