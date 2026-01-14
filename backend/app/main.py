"""CityPulse Backend API."""

import os
from pathlib import Path
import logging
import uuid
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud
from app.ai_workflow.workflow import run_backboard_ai, ai_followup
from app.database import get_db
from app.schemas import ReportInDB, Report, ReportUpdate, ReportFollowup
from app.validators import validate_images

logger = logging.getLogger(__name__)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="CityPulse API", version="1.0.0")

# TODO: tighten origins/methods/headers for prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Health check endpoint - required for Docker.
    Tries a trivial DB query; returns 503 if connection fails.
    """
    try:
        # Import inline to avoid circulars during app startup
        from sqlalchemy import create_engine, text
        from app.config import get_settings

        settings = get_settings()
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "service": "citypulse-backend",
            "database": "ok",
        }
    except Exception as exc:
        # Surface an unhealthy status for Docker healthcheck
        logger.error("Health check failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "citypulse-backend",
                "database": "error",
                "error": "database connection failed",
            },
        ) from None


@app.get("/")
def root():
    return {"message": "CityPulse API", "docs": "/docs"}


@app.post("/reports", response_model=ReportInDB)
async def create_report(
    title: str = Form(...),
    description: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    issue_images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Create a new report."""
    validate_images(issue_images)
    saved_filenames = []
    for file in issue_images:
        contents = await file.read()
        filename = f"{uuid.uuid4()}_{file.filename}"

        # Save to local storage (or S3, etc.)
        with open(UPLOAD_DIR / filename, "wb") as f:
            f.write(contents)
        saved_filenames.append(filename)
    
    input_report = Report(
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        report_images=saved_filenames
    )

    report_id = uuid.uuid4()

    try:
        thread_id, creation_time, ai_response = run_backboard_ai(
            description=description,
            latitude=latitude,
            longitude=longitude,
            image_files=issue_images,
        )
        if thread_id is None or creation_time is None or ai_response == {}:
            logger.error("AI workflow returned an invalid response")
            raise HTTPException(status_code=502, detail="AI workflow failed")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in AI workflow")
        raise HTTPException(status_code=502, detail="AI workflow failed") from None

    try:
        report = crud.create_report(
            db=db,
            user_report=input_report,
            ai_response=ai_response,
            report_id=report_id,
            thread_id=thread_id,
            creation_time=creation_time,
        )
    except Exception:
        logger.exception("Failed to persist report")
        raise HTTPException(status_code=500, detail="Failed to create report")

    return report

@app.post("/reports/{report_id}/followup")
def make_followup(
    report_id: UUID,
    answers: ReportFollowup,
    db: Session = Depends(get_db)
):
    report = crud.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    clarification = answers.answers
    result = ai_followup(
        thread_id=report.thread_id,
        description=clarification.get("description"),
        latitude=clarification.get("latitude"),
        longitude=clarification.get("longitude"),
        image_files=report
    )


@app.get("/reports", response_model=List[ReportInDB])
def list_reports(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all reports with optional filtering."""
    return crud.get_reports(db=db, status_filter=status_filter, priority_filter=priority_filter, category_filter=category_filter)


@app.get("/reports/{report_id}", response_model=ReportInDB)
def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a single report by ID."""
    report = crud.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# TODO: add authentication middleware and role check
@app.put("/reports/{report_id}", response_model=ReportInDB)
def update_report(
    report_id: UUID,
    updated_report: ReportUpdate,
    db: Session = Depends(get_db),
):
    """Update a report."""
    if report_id != updated_report.report_id:
        raise HTTPException(status_code=400, detail="Path report_id does not match body report_id")

    report = crud.update_report(
        db=db,
        report_id=updated_report.report_id,
        new_title=updated_report.title,
        new_description=updated_report.description,
        new_status=updated_report.status,
    )

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.delete("/reports/{report_id}", status_code=204)
def delete_report(
    report_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a report."""
    deleted = crud.delete_report(db=db, report_id=report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return None
