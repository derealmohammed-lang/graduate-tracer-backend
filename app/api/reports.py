from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])

SUPPORTED_TYPES = {"graduate_roster"}
SUPPORTED_FORMATS = {"pdf", "excel"}


@router.get("/generate")
def generate_report(
    report_type: str = Query(default="graduate_roster", alias="type"),
    report_format: str = Query(default="pdf", alias="format"),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    if report_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported report type. Supported: {sorted(SUPPORTED_TYPES)}")
    if report_format not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format. Supported: {sorted(SUPPORTED_FORMATS)}")

    # Only one report type is wired up today; add more branches here as
    # additional report types (Employment Outcomes, Survey Summary, Program
    # Performance) are implemented in report_service.
    if report_format == "pdf":
        buffer = report_service.generate_graduate_roster_pdf(db)
        media_type = "application/pdf"
        filename = "graduate_roster.pdf"
    else:
        buffer = report_service.generate_graduate_roster_excel(db)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "graduate_roster.xlsx"

    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
