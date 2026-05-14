from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Allow `uvicorn main:app --reload` from the backend directory by making
# the project root importable so `backend.*` absolute imports resolve.
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.db import lifespan
from backend.routes.academics.attendance import router as attendance_router
from backend.routes.academics.exams import router as exams_router
from backend.routes.academics.facility import router as facility_router
from backend.routes.academics.placement import router as placement_router
from backend.routes.academics.timetable import router as timetable_router
from backend.routes.analytics import router as analytics_router
from backend.routes.notifications import router as notifications_router
from backend.routes.payroll import router as payroll_router
from backend.routes.payroll_and_development import router as payroll_dev_router
from backend.routes.settings import router as settings_router
from backend.routes.staff import router as staff_router
from backend.routes.faculty import router as faculty_router
from backend.routes.faculty_management import router as faculty_mgmt_router
from backend.routes.faculty_360_feedback import router as faculty_feedback_router
from backend.routes.faculty_skills import router as faculty_skills_router
from backend.routes.faculty_mentorship import router as faculty_mentorship_router
from backend.routes.faculty_research import router as faculty_research_router
from backend.routes.faculty_compliance import router as faculty_compliance_router
from backend.routes.faculty_okr import router as faculty_okr_router
from backend.routes.faculty_publications import router as faculty_publications_router
from backend.routes.students import router as students_router
from backend.routes.administration.admissions import router as admissions_router
from backend.routes.administration.fees import router as fees_router
from backend.routes.administration.invoices import router as invoices_router
PORT = int(os.getenv("PORT", 5000))

app = FastAPI(title="CMS API", lifespan=lifespan)


def _parse_origins(value: Optional[str]):
    if not value:
        return []
    return [origin.strip() for origin in value.split(",") if origin.strip()]


configured_origins = _parse_origins(os.getenv("CORS_ORIGINS"))
default_origins = [
    "https://cms1-weof.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
allowed_origins = configured_origins or default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Serve Vite Frontend
# -------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = BASE_DIR / "frontend" / "dist"
DIST_ASSETS_DIR = DIST_DIR / "assets"
DIST_INDEX_FILE = DIST_DIR / "index.html"

if DIST_ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_ASSETS_DIR)), name="assets")


@app.get("/")
async def serve_frontend():
    if DIST_INDEX_FILE.exists():
        return FileResponse(str(DIST_INDEX_FILE))
    return {
        "message": "Frontend build not found. Run `npm run build` to serve static UI from FastAPI, or run Vite dev server for frontend development."
    }

app.include_router(staff_router)
app.include_router(faculty_router)
app.include_router(faculty_mgmt_router)
app.include_router(faculty_feedback_router)
app.include_router(faculty_skills_router)
app.include_router(faculty_mentorship_router)
app.include_router(faculty_research_router)
app.include_router(faculty_compliance_router)
app.include_router(faculty_okr_router)
app.include_router(faculty_publications_router)
app.include_router(payroll_router)
app.include_router(payroll_dev_router)
app.include_router(analytics_router)
app.include_router(exams_router)
app.include_router(timetable_router)
app.include_router(attendance_router)
app.include_router(placement_router)
app.include_router(facility_router)
app.include_router(notifications_router)
app.include_router(settings_router)
app.include_router(students_router)
app.include_router(admissions_router)
app.include_router(admissions_router, prefix="/api")
app.include_router(fees_router)
app.include_router(invoices_router)

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    if full_path.startswith("api") or full_path.startswith("docs"):
        raise HTTPException(status_code=404)
    if DIST_INDEX_FILE.exists():
        return FileResponse(str(DIST_INDEX_FILE))
    raise HTTPException(status_code=404, detail="Frontend build not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000)
