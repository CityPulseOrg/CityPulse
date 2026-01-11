"""
CityPulse Backend API

================================================================================
TODO: Backend team (Zak/Bala) - Implement the FastAPI application here.

REQUIREMENTS:
1. Create FastAPI app instance
2. Add CORS middleware (frontend needs to call this API)
3. Wire up database connection from app/database.py
4. Implement /health endpoint (REQUIRED for Docker healthcheck)
   - Must return JSON: {"status": "healthy", "service": "citypulse-backend"}
   - Should test database connectivity
5. Implement your report endpoints (POST /reports, GET /reports, etc.)
6. Integrate Backboard AI workflow calls using config from app/config.py

EXAMPLE MINIMAL SETUP:
    from fastapi import FastAPI
    app = FastAPI(title="CityPulse API")

    @app.get("/health")
    def health():
        return {"status": "healthy", "service": "citypulse-backend"}

DOCS: use the Fast APi documentation: https://fastapi.tiangolo.com/tutorial/first-steps/
================================================================================
"""

import uuid
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import logging
logger = logging.getLogger(__name__)
from typing import Optional, List
from .ai_workflow.workflow import run_backboard_ai
from . import crud
from .schemas import *
from .validators import validate_images

app = FastAPI(title="CityPulse API", version="1.0.0")

#TODO: will need to change origins, method and headers for prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#TODO: In-memory store for now (swap for DB once models are ready)
reportsDb: dict = {}


@app.get("/health")
def health():
    """Health check endpoint - required for Docker."""
    return {"status": "healthy", "service": "citypulse-backend"}


@app.get("/")
def root():
    return {"message": "CityPulse API", "docs": "/docs"}


@app.post("/reports")
def create_report(
    title: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    issueImages: List[UploadFile] = File(...),
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

    reportId = uuid.uuid4()

    try:
        threadId, creationTime, aiResponse = run_backboard_ai(
            description=description,
            imageFiles=issueImages
        )
        if threadId is None or creationTime is None or aiResponse == {}:
            logger.error("Sorry, the AI workflow returned an invalid response")
            raise HTTPException(status_code=502, detail="AI workflow failed")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in AI workflow")
        raise HTTPException(status_code=502, detail="AI workflow failed")

    report = crud.create_report(
        reportsDb,
        userReport,
        aiResponse,
        reportId,
        threadId,
        creationTime
    )

    return report


@app.get("/reports")
def list_reports(
    statusFilter: Optional[str] = None
):
    """List all reports."""
    return crud.get_reports(reportsDb, statusFilter)


@app.get("/reports/{reportId}")
def get_report(
        reportId: UUID
):
    """Get a single report by ID."""
    report = crud.get_report(
        db=reportsDb,
        issue_id=reportId
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

#TODO: add authentication middleware and role check
@app.put("/reports/{report_id}")
def update_report_handler(
        report_id: UUID
        updated_report: ReportUpdate
):
    """Update a report."""
    if report_id != updated_report.report_id:
        raise HTTPException(status_code=400, detail="Path report_id does not match body report_id")
    report = crud.update_report(
        db=reportsDb,
        report_id=updated_report.report_id,
        new_title=updated_report.title,
        new_description=updated_report.description,
        new_status=updated_report.status
    )

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.delete("/reports/{reportId}")
def delete_report_handler(reportId: UUID):
    """Delete a report."""
    report_deleted = crud.delete_report(
        db=reportsDb,
        report_id=reportId,
    )

    if report_deleted is None or report_deleted is False:
        raise HTTPException(status_code=404, detail="Report not found")
    return report_deleted
