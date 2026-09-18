import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import require_admin, require_super_admin
from app.core.database import get_db
from app.core.security import hash_password
from app.models.academic import Department, GraduationRecord, Program
from app.models.audit import AuditLog
from app.models.business import Business
from app.models.certification import Certification
from app.models.education import EducationRecord
from app.models.employment import EmploymentRecord
from app.models.graduate import Graduate
from app.models.user import User, UserRole
from app.schemas.business import BusinessOut
from app.schemas.certification import CertificationOut
from app.schemas.education import EducationRecordOut
from app.schemas.employment import EmploymentRecordOut
from app.schemas.admin import (
    AdministratorCreate,
    AdministratorOut,
    AdministratorStatusUpdate,
    AdminDashboardStats,
    AuditLogOut,
    DepartmentCreate,
    DepartmentOut,
    DepartmentUpdate,
    GraduateSummaryOut,
    ProgramCreate,
    ProgramOut,
    ProgramUpdate,
)
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])


# ---------------------------------------------------------------------------
# Dashboard & graduate roster (Administrator + Super Administrator)
# ---------------------------------------------------------------------------

@router.get("/dashboard", response_model=AdminDashboardStats)
def dashboard(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return admin_service.get_dashboard_stats(db)


@router.get("/statistics", response_model=AdminDashboardStats)
def statistics(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    # Alias of /dashboard today; kept separate per the blueprint's endpoint
    # list in case dashboard and statistics diverge later (e.g. statistics
    # gains date-range filters).
    return admin_service.get_dashboard_stats(db)


@router.get("/graduates", response_model=list[GraduateSummaryOut])
def list_graduates(
    search: str | None = Query(default=None, description="Search by name or admission number"),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    query = db.query(Graduate).join(User, Graduate.user_id == User.id)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                Graduate.first_name.ilike(like),
                Graduate.last_name.ilike(like),
                Graduate.admission_number.ilike(like),
            )
        )

    graduates = query.all()
    results = []
    for grad in graduates:
        latest_program = (
            db.query(Program.name)
            .join(GraduationRecord, GraduationRecord.program_id == Program.id)
            .filter(GraduationRecord.graduate_id == grad.id)
            .order_by(GraduationRecord.graduation_year.desc())
            .first()
        )
        current_employment = (
            db.query(EmploymentRecord)
            .filter(EmploymentRecord.graduate_id == grad.id, EmploymentRecord.is_current.is_(True))
            .first()
        )
        results.append(
            GraduateSummaryOut(
                id=grad.id,
                full_name=grad.full_name,
                admission_number=grad.admission_number,
                email=grad.email,
                program=latest_program[0] if latest_program else None,
                employment_status=current_employment.employment_status.value if current_employment else None,
                is_active=grad.user.is_active,
            )
        )
    return results


# ---------------------------------------------------------------------------
# Per-graduate record views (used by the admin Graduate Details screen)
# ---------------------------------------------------------------------------

@router.get("/graduates/{graduate_id}/employment", response_model=list[EmploymentRecordOut])
def get_graduate_employment(graduate_id: uuid.UUID, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return db.query(EmploymentRecord).filter(EmploymentRecord.graduate_id == graduate_id).all()


@router.get("/graduates/{graduate_id}/education", response_model=list[EducationRecordOut])
def get_graduate_education(graduate_id: uuid.UUID, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return db.query(EducationRecord).filter(EducationRecord.graduate_id == graduate_id).all()


@router.get("/graduates/{graduate_id}/certifications", response_model=list[CertificationOut])
def get_graduate_certifications(graduate_id: uuid.UUID, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return db.query(Certification).filter(Certification.graduate_id == graduate_id).all()


@router.get("/graduates/{graduate_id}/businesses", response_model=list[BusinessOut])
def get_graduate_businesses(graduate_id: uuid.UUID, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return db.query(Business).filter(Business.graduate_id == graduate_id).all()


# ---------------------------------------------------------------------------
# Cross-graduate record views (used by the admin management list screens)
# ---------------------------------------------------------------------------

def _with_graduate_name(db: Session, rows: list, graduate_id_attr: str = "graduate_id") -> list[dict]:
    """Attach `graduate_name` / `admission_number` to a list of ORM rows that
    each have a `graduate_id`, without requiring a strict response schema.
    """
    graduate_ids = {getattr(r, graduate_id_attr) for r in rows}
    graduates = {g.id: g for g in db.query(Graduate).filter(Graduate.id.in_(graduate_ids)).all()} if graduate_ids else {}

    results = []
    for row in rows:
        grad = graduates.get(getattr(row, graduate_id_attr))
        item = {c.name: getattr(row, c.name) for c in row.__table__.columns}
        # Serialize non-JSON-native types.
        for key, value in list(item.items()):
            if hasattr(value, "isoformat"):
                item[key] = value.isoformat()
            elif hasattr(value, "value"):  # enums
                item[key] = value.value
            elif not isinstance(value, (str, int, float, bool, type(None))):
                item[key] = str(value)
        item["graduate_name"] = grad.full_name if grad else "Unknown"
        item["admission_number"] = grad.admission_number if grad else None
        results.append(item)
    return results


@router.get("/employment")
def list_all_employment(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    rows = db.query(EmploymentRecord).order_by(EmploymentRecord.start_date.desc()).all()
    return _with_graduate_name(db, rows)


@router.get("/education")
def list_all_education(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    rows = db.query(EducationRecord).all()
    return _with_graduate_name(db, rows)


@router.get("/certifications")
def list_all_certifications(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    rows = db.query(Certification).all()
    return _with_graduate_name(db, rows)


@router.get("/businesses")
def list_all_businesses(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    rows = db.query(Business).all()
    return _with_graduate_name(db, rows)


# ---------------------------------------------------------------------------
# Super Admin: Departments
# ---------------------------------------------------------------------------

@router.get("/departments", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return db.query(Department).all()


@router.post("/departments", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentCreate, db: Session = Depends(get_db), _admin=Depends(require_super_admin)):
    department = Department(**payload.model_dump())
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.put("/departments/{department_id}", response_model=DepartmentOut)
def update_department(department_id: uuid.UUID, payload: DepartmentUpdate, db: Session = Depends(get_db), _admin=Depends(require_super_admin)):
    department = db.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(department, field, value)
    db.commit()
    db.refresh(department)
    return department


# ---------------------------------------------------------------------------
# Super Admin: Programs
# ---------------------------------------------------------------------------

@router.get("/programs", response_model=list[ProgramOut])
def list_programs(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return db.query(Program).all()


@router.post("/programs", response_model=ProgramOut, status_code=status.HTTP_201_CREATED)
def create_program(payload: ProgramCreate, db: Session = Depends(get_db), _admin=Depends(require_super_admin)):
    program = Program(**payload.model_dump())
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@router.put("/programs/{program_id}", response_model=ProgramOut)
def update_program(program_id: uuid.UUID, payload: ProgramUpdate, db: Session = Depends(get_db), _admin=Depends(require_super_admin)):
    program = db.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(program, field, value)
    db.commit()
    db.refresh(program)
    return program


# ---------------------------------------------------------------------------
# Super Admin: Administrators
# ---------------------------------------------------------------------------

@router.get("/administrators", response_model=list[AdministratorOut])
def list_administrators(db: Session = Depends(get_db), _admin=Depends(require_super_admin)):
    return db.query(User).filter(User.role.in_([UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR])).all()


@router.post("/administrators", response_model=AdministratorOut, status_code=status.HTTP_201_CREATED)
def create_administrator(payload: AdministratorCreate, db: Session = Depends(get_db), _admin=Depends(require_super_admin)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

    admin_user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user


@router.put("/administrators/{admin_id}/status", response_model=AdministratorOut)
def update_administrator_status(admin_id: uuid.UUID, payload: AdministratorStatusUpdate, db: Session = Depends(get_db), _admin=Depends(require_super_admin)):
    admin_user = db.get(User, admin_id)
    if not admin_user or admin_user.role not in (UserRole.ADMINISTRATOR, UserRole.SUPER_ADMINISTRATOR):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Administrator not found")
    admin_user.is_active = payload.is_active
    db.commit()
    db.refresh(admin_user)
    return admin_user


# ---------------------------------------------------------------------------
# Super Admin: Audit Logs
# ---------------------------------------------------------------------------

@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(db: Session = Depends(get_db), _admin=Depends(require_super_admin)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
    user_ids = {log.user_id for log in logs if log.user_id}
    users_by_id = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    return [
        AuditLogOut(
            id=log.id,
            user_id=log.user_id,
            user_name=(users_by_id[log.user_id].full_name or users_by_id[log.user_id].email) if log.user_id in users_by_id else None,
            action=log.action,
            table_name=log.table_name,
            record_id=log.record_id,
            created_at=log.created_at,
        )
        for log in logs
    ]
