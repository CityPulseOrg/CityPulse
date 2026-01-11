"""CityPulse Backend API."""

import logging
import uuid
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud
from app.ai_workflow.workflow import run_backboard_ai
from app.database import get_db
from app.schemas import IssueOut, Report, ReportUpdate
from app.validators import validate_images

logger = logging.getLogger(__name__)

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
    """Health check endpoint - required for Docker."""
    return {"status": "healthy", "service": "citypulse-backend"}


@app.get("/")
def root():
    return {"message": "CityPulse API", "docs": "/docs"}


@app.post("/reports", response_model=IssueOut)
def create_report(
    title: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    issueImages: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Create a new report."""
    validate_images(issueImages)

    userReport = Report(
        title=title,
        description=description,
        address=address,
        city=city,
        latitude=latitude,
        longitude=longitude,
    )

    report_id = uuid.uuid4()

    try:
        threadId, creationTime, aiResponse = run_backboard_ai(
            description=description,
            imageFiles=issueImages,
        )
        if threadId is None or creationTime is None or aiResponse == {}:
            logger.error("AI workflow returned an invalid response")
            raise HTTPException(status_code=502, detail="AI workflow failed")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in AI workflow")
        raise HTTPException(status_code=502, detail="AI workflow failed")

    try:
        report = crud.create_report(
            db=db,
            user_report=userReport,
            ai_response=aiResponse,
            report_id=report_id,
            thread_id=threadId,
            creation_time=creationTime,
        )
    except Exception:
        logger.exception("Failed to persist report")
        raise HTTPException(status_code=500, detail="Failed to create report")

    return report


@app.get("/reports", response_model=List[IssueOut])
def list_reports(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all reports."""
    return crud.get_reports(db=db, status_filter=status)


@app.get("/reports/{id}", response_model=IssueOut)
def get_report(
    id: UUID,
    db: Session = Depends(get_db),
):
    """Get a single report by ID."""
    report = crud.get_report(db=db, report_id=id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# TODO: add authentication middleware and role check
@app.put("/reports/{id}", response_model=IssueOut)
def update_report(
    id: UUID,
    updated_report: ReportUpdate,
    db: Session = Depends(get_db),
):
    """Update a report."""
    if id != updated_report.report_id:
        raise HTTPException(status_code=400, detail="Path id does not match body report_id")

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


@app.delete("/reports/{id}", status_code=204)
def delete_report(
    id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a report."""
    deleted = crud.delete_report(db=db, report_id=id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return None
