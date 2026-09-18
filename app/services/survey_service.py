import json
import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.graduate import Graduate
from app.models.survey import (
    QuestionOption,
    QuestionType,
    Survey,
    SurveyAnswer,
    SurveyQuestion,
    SurveyResponse,
)
from app.schemas.survey import SurveyCreate, SurveyResponseSubmit


def create_survey(db: Session, data: SurveyCreate, created_by: uuid.UUID) -> Survey:
    survey = Survey(
        title=data.title,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        status=data.status,
        target_program=data.target_program,
        target_year=data.target_year,
        created_by=created_by,
    )
    db.add(survey)
    db.flush()

    for q in data.questions:
        question = SurveyQuestion(
            survey_id=survey.id,
            question=q.question,
            question_type=q.question_type,
            is_required=q.is_required,
            display_order=q.display_order,
        )
        db.add(question)
        db.flush()

        for opt in q.options:
            db.add(QuestionOption(question_id=question.id, option_text=opt.option_text, display_order=opt.display_order))

    db.commit()
    db.refresh(survey)
    return survey


def submit_response(db: Session, survey: Survey, graduate: Graduate, payload: SurveyResponseSubmit) -> SurveyResponse:
    existing = (
        db.query(SurveyResponse)
        .filter(SurveyResponse.survey_id == survey.id, SurveyResponse.graduate_id == graduate.id)
        .first()
    )
    if existing:
        raise ValueError("You have already submitted a response to this survey")

    response = SurveyResponse(survey_id=survey.id, graduate_id=graduate.id)
    db.add(response)
    db.flush()

    for ans in payload.answers:
        db.add(SurveyAnswer(response_id=response.id, question_id=ans.question_id, answer=ans.answer))

    db.commit()
    db.refresh(response)
    return response


def compute_results(db: Session, survey: Survey, total_targeted: int) -> dict:
    total_responses = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey.id).count()
    response_rate = (total_responses / total_targeted) if total_targeted else 0.0

    breakdowns = []
    for question in survey.questions:
        answers = (
            db.query(SurveyAnswer)
            .filter(SurveyAnswer.question_id == question.id)
            .all()
        )

        if question.question_type in (QuestionType.SINGLE_CHOICE, QuestionType.YES_NO):
            counts = {opt.option_text: 0 for opt in question.options} if question.options else {}
            for a in answers:
                counts[a.answer] = counts.get(a.answer, 0) + 1
            breakdowns.append({
                "question_id": question.id,
                "question": question.question,
                "question_type": question.question_type,
                "counts": counts,
                "text_answers": [],
            })
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            counts = {opt.option_text: 0 for opt in question.options} if question.options else {}
            for a in answers:
                try:
                    selected = json.loads(a.answer)
                except (json.JSONDecodeError, TypeError):
                    selected = [a.answer]
                for s in selected:
                    counts[s] = counts.get(s, 0) + 1
            breakdowns.append({
                "question_id": question.id,
                "question": question.question,
                "question_type": question.question_type,
                "counts": counts,
                "text_answers": [],
            })
        elif question.question_type == QuestionType.RATING:
            counts = {str(i): 0 for i in range(1, 6)}
            for a in answers:
                if a.answer in counts:
                    counts[a.answer] += 1
            breakdowns.append({
                "question_id": question.id,
                "question": question.question,
                "question_type": question.question_type,
                "counts": counts,
                "text_answers": [],
            })
        else:  # SHORT_ANSWER / LONG_ANSWER
            breakdowns.append({
                "question_id": question.id,
                "question": question.question,
                "question_type": question.question_type,
                "counts": {},
                "text_answers": [a.answer for a in answers],
            })

    return {
        "survey_id": survey.id,
        "title": survey.title,
        "total_responses": total_responses,
        "total_targeted": total_targeted,
        "response_rate": round(response_rate, 4),
        "question_breakdowns": breakdowns,
    }


def is_survey_open(survey: Survey, today: date | None = None) -> bool:
    today = today or date.today()
    return survey.status == "Active" and survey.start_date <= today <= survey.end_date
