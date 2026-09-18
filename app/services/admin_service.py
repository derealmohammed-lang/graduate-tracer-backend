from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.employment import EmploymentRecord, EmploymentStatus
from app.models.graduate import Graduate
from app.models.survey import Survey, SurveyResponse


def get_dashboard_stats(db: Session) -> dict:
    total_graduates = db.query(Graduate).count()
    total_active_surveys = db.query(Survey).filter(Survey.status == "Active").count()

    # Response rate across all surveys: total responses / (graduates * surveys).
    total_surveys = db.query(Survey).count()
    total_responses = db.query(SurveyResponse).count()
    possible_responses = total_graduates * total_surveys
    overall_response_rate = round(total_responses / possible_responses, 4) if possible_responses else 0.0

    breakdown_rows = (
        db.query(EmploymentRecord.employment_status, func.count(EmploymentRecord.id))
        .filter(EmploymentRecord.is_current.is_(True))
        .group_by(EmploymentRecord.employment_status)
        .all()
    )
    breakdown = {status.value: 0 for status in EmploymentStatus}
    for status_value, count in breakdown_rows:
        breakdown[status_value.value] = count

    return {
        "total_graduates": total_graduates,
        "total_active_surveys": total_active_surveys,
        "overall_response_rate": overall_response_rate,
        "employment_status_breakdown": breakdown,
    }
