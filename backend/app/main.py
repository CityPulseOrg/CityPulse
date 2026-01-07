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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CityPulse API", version="1.0.0")
#TODO: will need to change origins, method and headers for prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#TODO: In-memory store for now (swap for DB once models are ready)
reports_db: dict = {}


@app.get("/health")
def health():
    """Health check endpoint - required for Docker."""
    return {"status": "healthy", "service": "citypulse-backend"}


@app.get("/")
def root():
    return {"message": "CityPulse API", "docs": "/docs"}


@app.post("/reports")
def create_report(
    title: str,
    description: str,
    address: str,
    city: str,
    latitude: float | None = None,
    longitude: float | None = None,
):
    """Create a new report."""
    report_id = str(uuid.uuid4())
    report = {
        "id": report_id,
        "title": title,
        "description": description,
        "address": address,
        "city": city,
        "latitude": latitude,
        "longitude": longitude,
        "status": "open",
    }
    reports_db[report_id] = report
    return report


@app.get("/reports")
def list_reports():
    """List all reports."""
    return list(reports_db.values())


@app.get("/reports/{report_id}")
def get_report(report_id: str):
    """Get a single report by ID."""
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    return reports_db[report_id]


@app.put("/reports/{report_id}")
def update_report(report_id: str, title: str | None = None, description: str | None = None, status: str | None = None):
    """Update a report."""
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    report = reports_db[report_id]
    if title:
        report["title"] = title
    if description:
        report["description"] = description
    if status:
        report["status"] = status
    return report


@app.delete("/reports/{report_id}")
def delete_report(report_id: str):
    """Delete a report."""
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    del reports_db[report_id]
    return {"detail": "Report deleted"}
