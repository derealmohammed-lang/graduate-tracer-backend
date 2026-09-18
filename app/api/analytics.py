from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.academic import GraduationRecord, Program
from app.services import admin_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/programs")
def graduates_by_program(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    rows = (
        db.query(Program.name, Program.code, func.count(GraduationRecord.id))
        .join(GraduationRecord, GraduationRecord.program_id == Program.id, isouter=True)
        .group_by(Program.id, Program.name, Program.code)
        .all()
    )
    return [{"program": name, "code": code, "graduate_count": count} for name, code, count in rows]


@router.get("/employment-trend")
def employment_trend(_admin=Depends(require_admin)):
    # TODO: this requires a time-series snapshot table (e.g. a scheduled job
    # that records the employment-status breakdown monthly) since employment
    # status is currently only stored as a "current" flag, not a history of
    # rates over time. Wire that table up, then replace this stub.
    return {"message": "Employment trend requires historical snapshots; not yet implemented.", "data": []}


@router.get("/engagement")
def survey_engagement(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    stats = admin_service.get_dashboard_stats(db)
    return {
        "active_surveys": stats["total_active_surveys"],
        "overall_response_rate": stats["overall_response_rate"],
    }
