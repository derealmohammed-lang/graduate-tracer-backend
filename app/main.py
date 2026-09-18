from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import admin, analytics, auth, businesses, certifications, education, employment, graduates, notifications, public, reports, surveys, users
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for the Graduate Tracer application.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_path = Path(settings.UPLOAD_DIR)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(public.router)
app.include_router(graduates.router)
app.include_router(employment.router)
app.include_router(education.router)
app.include_router(certifications.router)
app.include_router(businesses.router)
app.include_router(surveys.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(reports.router)
app.include_router(analytics.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}
