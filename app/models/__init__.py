"""Import every model so `Base.metadata` (used by Alembic autogenerate and
`create_all` in dev/tests) is aware of all tables, and so relationship()
string references resolve correctly.
"""

from app.models.user import User, UserRole  # noqa: F401
from app.models.graduate import Graduate  # noqa: F401
from app.models.academic import Department, Program, GraduationRecord  # noqa: F401
from app.models.employment import EmploymentRecord, EmploymentStatus  # noqa: F401
from app.models.education import EducationRecord  # noqa: F401
from app.models.certification import Certification  # noqa: F401
from app.models.business import Business  # noqa: F401
from app.models.survey import (  # noqa: F401
    Survey,
    SurveyQuestion,
    QuestionOption,
    SurveyResponse,
    SurveyAnswer,
    QuestionType,
)
from app.models.notification import Notification, UserNotification  # noqa: F401
from app.models.password_reset import PasswordReset  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.file import FileRecord  # noqa: F401
