"""CityPulse Backend API."""

import logging
import uuid
<<<<<<< Updated upstream
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
=======
from fastapi import FastAPI, HTTPException, Form, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from sqlalchemy.orm import Session
from ai_workflow.workflow import *
from crud import *
from schemas import *
from database import get_db
from app import models
>>>>>>> Stashed changes

app = FastAPI(title="CityPulse API", version="1.0.0")

# TODO: tighten origins/methods/headers for prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< Updated upstream
=======
def analyze_priority_and_risk(description: str, category: Optional[str] = None, db: Session = None) -> tuple[str, str, int]:
    """
    Analyze issue description to determine priority and risk level.
    Returns: (priority, risk, base_score)
    """
    description_lower = description.lower()
    score = 0

    # High priority keywords (immediate danger/safety)
    high_priority_keywords = [
        'emergency', 'danger', 'hazard', 'unsafe', 'broken', 'collapse', 'falling',
        'fire', 'explosion', 'gas leak', 'water main break', 'power outage',
        'blocked', 'obstructed', 'traffic accident', 'injury', 'medical'
    ]

    # Medium priority keywords (infrastructure issues)
    medium_priority_keywords = [
        'pothole', 'crack', 'damage', 'leak', 'flood', 'sewage', 'garbage',
        'trash', 'litter', 'graffiti', 'vandalism', 'broken glass', 'needle'
    ]

    # Low priority keywords (maintenance/cosmetic)
    low_priority_keywords = [
        'dirty', 'stained', 'faded', 'overgrown', 'weeds', 'paint', 'cosmetic'
    ]

    # Calculate base score from keywords
    for keyword in high_priority_keywords:
        if keyword in description_lower:
            score += 3

    for keyword in medium_priority_keywords:
        if keyword in description_lower:
            score += 2

    for keyword in low_priority_keywords:
        if keyword in description_lower:
            score += 1

    # Category-based adjustments
    if category:
        category_lower = category.lower()
        if 'lighting' in category_lower or 'street light' in category_lower:
            score += 2  # Street lighting issues can be safety concerns
        elif 'traffic' in category_lower or 'sign' in category_lower:
            score += 1  # Traffic-related issues

    # Length-based scoring (longer descriptions might indicate more serious issues)
    if len(description) > 200:
        score += 1

    # Check for similar recent reports (clustering effect)
    if db:
        try:
            # Look for similar reports in the last 30 days
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)

            # Simple similarity check based on category and location proximity
            similar_reports = db.query(models.IssueTable).filter(
                models.IssueTable.category == category,
                models.IssueTable.creationTime >= thirty_days_ago,
                models.IssueTable.status.in_(['open', 'in_progress'])
            ).count()

            # Increase priority if multiple similar reports exist
            if similar_reports >= 3:
                score += 2
            elif similar_reports >= 1:
                score += 1

        except Exception as e:
            print(f"Error checking similar reports: {e}")

    # Determine priority and risk levels
    if score >= 6:
        priority = "High"
        risk = "Critical"
    elif score >= 4:
        priority = "Medium"
        risk = "High"
    elif score >= 2:
        priority = "Low"
        risk = "Medium"
    else:
        priority = "Low"
        risk = "Low"

    return priority, risk, score

>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    issue_images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Create a new report."""
    validate_images(issue_images)

=======
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    issueImages: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Create a new report with AI-powered priority and risk assessment."""

    # Run AI workflow to get category and other AI insights
    threadId, creationTime, aiResponse = run_backboard_ai(description=description,
                                                          imageFiles=issueImages)

    # Extract category from AI response
    category = aiResponse.get('category') if aiResponse else None

    # Analyze priority and risk using AI
    priority, risk, base_score = analyze_priority_and_risk(description, category, db)

    # Create the report with AI-enriched data
>>>>>>> Stashed changes
    userReport = Report(
        title=title,
        description=description,
        address=address,
        city=city,
        latitude=latitude,
        longitude=longitude,
    )

<<<<<<< Updated upstream
    report_id = uuid.uuid4()

    try:
        thread_id, creation_time, ai_response = run_backboard_ai(
            description=description,
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
            user_report=userReport,
            ai_response=ai_response,
            report_id=report_id,
            thread_id=thread_id,
            creation_time=creation_time,
        )
    except Exception:
        logger.exception("Failed to persist report")
        raise HTTPException(status_code=500, detail="Failed to create report")
=======
    report = crud.create_report_with_ai(
        db=db,
        userReport=userReport,
        aiResponse=aiResponse,
        threadId=threadId,
        priority=priority,
        risk=risk,
        category=category
    )
>>>>>>> Stashed changes

    return report


@app.get("/reports", response_model=List[IssueOut])
def list_reports(
<<<<<<< Updated upstream
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all reports."""
    return crud.get_reports(db=db, status_filter=status)
=======
    statusFilter: Optional[str] = None,
    priorityFilter: Optional[str] = None,
    categoryFilter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all reports with optional filtering."""
    return crud.get_reports(db=db, statusFilter=statusFilter, priorityFilter=priorityFilter, categoryFilter=categoryFilter)
>>>>>>> Stashed changes


@app.get("/reports/{report_id}", response_model=IssueOut)
def get_report(
<<<<<<< Updated upstream
    report_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a single report by ID."""
    report = crud.get_report(db=db, report_id=report_id)
=======
    reportId: str,
    db: Session = Depends(get_db)
):
    """Get a single report by ID."""
    report = crud.get_report(db=db, issue_id=reportId)
>>>>>>> Stashed changes
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# TODO: add authentication middleware and role check
@app.put("/reports/{report_id}", response_model=IssueOut)
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
