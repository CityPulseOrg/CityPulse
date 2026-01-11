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
from typing import Optional, List
from ai_workflow.workflow import run_backboard_ai
from . import crud
from schemas import *

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
    userReport = Report(
        title=title,
        description=description,
        address=address,
        city=city,
        latitude=latitude,
        longitude=longitude,
    )

    reportId = str(uuid.uuid4())

    try:
        threadId, creationTime, aiResponse = run_backboard_ai(
        description=description,
        imageFiles=issueImages
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail="AI workflow failed") from e

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
        reportId: str
):
    """Get a single report by ID."""
    report = crud.get_report(
        db=reportsDb,
        issue_id=reportId
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.put("/reports/{reportId}")
def update_report_handler(
        reportId: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
):
    """Update a report."""
    report = crud.update_report(
        db=reportsDb,
        report_id=reportId,
        new_title=title,
        new_description=description,
        new_status=status
    )

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.delete("/reports/{reportId}")
def delete_report_handler(reportId: str):
    """Delete a report."""
    report_deleted = crud.delete_report(
        db=reportsDb,
        report_id=reportId,
    )

    if report_deleted is None or report_deleted is False:
        raise HTTPException(status_code=404, detail="Report not found")
    return report_deleted
