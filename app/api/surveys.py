import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_graduate, require_admin
from app.core.database import get_db
from app.models.graduate import Graduate
from app.models.survey import Survey
from app.schemas.survey import (
    SurveyCreate,
    SurveyListItem,
    SurveyOut,
    SurveyResponseSubmit,
    SurveyResponseOut,
    SurveyResultsOut,
)
from app.services import survey_service

router = APIRouter(prefix="/surveys", tags=["Surveys"])


@router.get("", response_model=list[SurveyListItem])
def list_surveys(graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    """Surveys visible to the signed-in graduate. Targeting filters (program,
    year) can be layered on here once graduate-facing targeting is needed;
    for now every graduate sees every survey."""
    from app.models.survey import SurveyResponse

    surveys = db.query(Survey).order_by(Survey.start_date.desc()).all()
    responded_ids = {
        r.survey_id
        for r in db.query(SurveyResponse.survey_id).filter(SurveyResponse.graduate_id == graduate.id).all()
    }

    return [
        SurveyListItem(
            id=s.id,
            title=s.title,
            description=s.description,
            start_date=s.start_date,
            end_date=s.end_date,
            status=s.status,
            has_responded=s.id in responded_ids,
        )
        for s in surveys
    ]


@router.get("/{survey_id}", response_model=SurveyOut)
def get_survey(survey_id: uuid.UUID, _graduate: Graduate = Depends(get_current_graduate), db: Session = Depends(get_db)):
    survey = db.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")
    return survey


@router.post("/{survey_id}/responses", response_model=SurveyResponseOut, status_code=status.HTTP_201_CREATED)
def submit_survey_response(
    survey_id: uuid.UUID,
    payload: SurveyResponseSubmit,
    graduate: Graduate = Depends(get_current_graduate),
    db: Session = Depends(get_db),
):
    survey = db.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")

    try:
        response = survey_service.submit_response(db, survey, graduate, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return response


@router.get("/{survey_id}/results", response_model=SurveyResultsOut)
def get_survey_results(survey_id: uuid.UUID, db: Session = Depends(get_db), _admin=Depends(require_admin)):
    survey = db.get(Survey, survey_id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey not found")

    # TODO: compute total_targeted from actual targeting criteria (program/
    # year/status) once that's stored; for now use the full graduate count.
    from app.models.graduate import Graduate as GraduateModel

    total_targeted = db.query(GraduateModel).count()
    results = survey_service.compute_results(db, survey, total_targeted)
    return results


@router.post("", response_model=SurveyOut, status_code=status.HTTP_201_CREATED)
def create_survey(payload: SurveyCreate, admin=Depends(require_admin), db: Session = Depends(get_db)):
    return survey_service.create_survey(db, payload, created_by=admin.id)
