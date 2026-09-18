import io

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy.orm import Session

from app.models.academic import GraduationRecord, Program
from app.models.employment import EmploymentRecord
from app.models.graduate import Graduate


def _roster_rows(db: Session) -> list[list[str]]:
    rows = [["Admission No.", "Name", "Program", "Employment Status", "Email"]]
    for grad in db.query(Graduate).all():
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
        rows.append([
            grad.admission_number,
            grad.full_name,
            latest_program[0] if latest_program else "-",
            current_employment.employment_status.value if current_employment else "-",
            grad.email or "-",
        ])
    return rows


def generate_graduate_roster_pdf(db: Session) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    rows = _roster_rows(db)
    table = Table(rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B5FFF")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FB")]),
            ]
        )
    )

    doc.build([
        Paragraph("Graduate Roster Report", styles["Title"]),
        Spacer(1, 12),
        table,
    ])
    buffer.seek(0)
    return buffer


def generate_graduate_roster_excel(db: Session) -> io.BytesIO:
    buffer = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Graduate Roster"

    for row in _roster_rows(db):
        ws.append(row)

    for i, column_cells in enumerate(ws.columns, start=1):
        max_length = max(len(str(cell.value)) for cell in column_cells if cell.value is not None) if any(cell.value for cell in column_cells) else 10
        ws.column_dimensions[column_cells[0].column_letter].width = max_length + 2

    wb.save(buffer)
    buffer.seek(0)
    return buffer
