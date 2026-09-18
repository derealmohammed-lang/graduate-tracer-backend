import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.survey import QuestionType


class QuestionOptionCreate(BaseModel):
    option_text: str
    display_order: int = 0


class QuestionOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    option_text: str
    display_order: int


class SurveyQuestionCreate(BaseModel):
    question: str
    question_type: QuestionType
    is_required: bool = True
    display_order: int = 0
    options: list[QuestionOptionCreate] = []


class SurveyQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    question: str
    question_type: QuestionType
    is_required: bool
    display_order: int
    options: list[QuestionOptionOut] = []


class SurveyCreate(BaseModel):
    title: str
    description: str | None = None
    start_date: date
    end_date: date
    target_program: str | None = None
    target_year: int | None = None
    status: str = "Draft"
    questions: list[SurveyQuestionCreate] = []


class SurveyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str | None
    start_date: date
    end_date: date
    status: str
    target_program: str | None
    target_year: int | None
    created_at: datetime
    questions: list[SurveyQuestionOut] = []


class SurveyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    title: str
    description: str | None
    start_date: date
    end_date: date
    status: str
    has_responded: bool = False


class SurveyAnswerSubmit(BaseModel):
    question_id: uuid.UUID
    answer: str  # For multi-select, the API expects a JSON-encoded list as a string


class SurveyResponseSubmit(BaseModel):
    answers: list[SurveyAnswerSubmit]


class SurveyResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    survey_id: uuid.UUID
    graduate_id: uuid.UUID
    submitted_at: datetime
    status: str


class QuestionResultBreakdown(BaseModel):
    question_id: uuid.UUID
    question: str
    question_type: QuestionType
    # For choice/rating questions: option/rating label -> response count.
    counts: dict[str, int] = {}
    # For open-ended questions: raw text answers.
    text_answers: list[str] = []


class SurveyResultsOut(BaseModel):
    survey_id: uuid.UUID
    title: str
    total_responses: int
    total_targeted: int
    response_rate: float
    question_breakdowns: list[QuestionResultBreakdown]
