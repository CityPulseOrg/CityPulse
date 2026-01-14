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
from . import crud
from . import schemas

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
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "citypulse-backend",
                "database": "error",
                "error": str(exc),
            },
        )



@app.get("/")
def root():
    return {"message": "CityPulse API", "docs": "/docs"}


@app.post("/reports")
def create_report(
    title: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    issueImages: List[UploadFile] = File(...),
):
    """Create a new report."""
    userReport = schemas.Report(
        title=title,
        description=description,
        address=address,
        city=city,
        latitude=latitude,
        longitude=longitude,
    )

    reportId = str(uuid.uuid4())
    # TODO: Implement AI workflow
    # threadId, creationTime, aiResponse = run_backboard_ai(description=description,
    #                                                       imageFiles=issueImages)
    threadId = None
    creationTime = None
    aiResponse = None
    report = crud.create_report(reportsDb,
                               userReport,
                               aiResponse,
                               reportId,
                               threadId,
                               creationTime)

    return report


@app.get("/reports")
def list_reports(
    statusFilter: Optional[str] = None
):
    """List all reports."""
    return crud.get_reports(reportsDb, statusFilter)


@app.get("/reports/{report_id}")
def get_report(
        report_id: str
):
    """Get a single report by ID."""
    report = crud.get_report(
        db=reportsDb,
        issue_id=report_id
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.put("/reports/{report_id}")
def update_report(
        report_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[str] = None
):
    """Update a report."""
    report = crud.get_report(
        db=reportsDb,
        issue_id=report_id
    )

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")



    return report


@app.delete("/reports/{report_id}")
def delete_report(report_id: str):
    """Delete a report."""
    if report_id not in reportsDb:
        raise HTTPException(status_code=404, detail="Report not found")
    del reportsDb[report_id]
    return {"detail": "Report deleted"}
