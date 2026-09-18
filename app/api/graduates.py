import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_graduate, require_admin
from app.core.database import get_db
from app.models.academic import Department, GraduationRecord, Program
from app.models.employment import EmploymentRecord
from app.models.graduate import Graduate
from app.schemas.graduate import GraduateOut, GraduateProfileOut, GraduateUpdate

router = APIRouter(prefix="/graduates", tags=["Graduates"])


def _build_profile(db: Session, graduate: Graduate) -> GraduateProfileOut:
    latest_grad_record = (
        db.query(GraduationRecord)
        .filter(GraduationRecord.graduate_id == graduate.id)
        .order_by(GraduationRecord.graduation_year.desc())
        .first()
    )
    program_name = None
    department_name = None
    graduation_year = None
    if latest_grad_record:
        graduation_year = latest_grad_record.graduation_year
        program = db.get(Program, latest_grad_record.program_id)
        if program:
            program_name = program.name
            department = db.get(Department, program.department_id)
            department_name = department.name if department else None

    current_employment = (
        db.query(EmploymentRecord)
        .filter(EmploymentRecord.graduate_id == graduate.id, EmploymentRecord.is_current.is_(True))
        .first()
    )

    # Simple weighted completion heuristic across the sections the app
    # surfaces on the dashboard. Adjust the weights/fields as the profile
    # form grows.
    filled = sum(
        1
        for value in [
            graduate.gender,
            graduate.date_of_birth,
            graduate.nationality,
            graduate.address,
            graduate.county,
            graduate.profile_photo,
            program_name,
            current_employment,
        ]
        if value
    )
    profile_completion = round(filled / 8, 2)

    return GraduateProfileOut(
        **GraduateOut.model_validate(graduate).model_dump(),
        program=program_name,
        department=department_name,
        graduation_year=graduation_year,
        employment_status=current_employment.employment_status.value if current_employment else None,
        current_position=current_employment.job_title if current_employment else None,
        profile_completion=profile_completion,
    )


@router.get("/me", response_model=GraduateProfileOut)
def get_my_profile(graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    return _build_profile(db, graduate)


@router.put("/me", response_model=GraduateProfileOut)
def update_my_profile(payload: GraduateUpdate, graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)

    if "email" in data and data["email"]:
        from app.models.user import User

        existing = (
            db.query(User)
            .filter(User.email == data["email"], User.id != graduate.user_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
        graduate.user.email = data["email"]

    if "phone" in data:
        graduate.user.phone = data["phone"] or None

    for field, value in data.items():
        setattr(graduate, field, value)

    db.commit()
    db.refresh(graduate)
    return _build_profile(db, graduate)


@router.get("/{graduate_id}", response_model=GraduateOut)
def get_graduate_by_id(graduate_id: uuid.UUID, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    graduate = db.get(Graduate, graduate_id)
    if not graduate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graduate not found")
    return graduate
