"""CityPulse Backend API."""

import os
from pathlib import Path
import logging
import uuid
from typing import List, Optional
from uuid import UUID
from threading import Thread

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud
from app.geocoding import reverse_geocode
from app.ai_workflow.workflow import run_backboard_ai, ai_followup
from app.ai_workflow.assistant import create_assistant
from app.database import get_db, engine
from app.schemas import ReportInDB, ReportResponse, Report, ReportUpdate, ReportFollowup, ClarificationQuestion
from app.background_tasks import clean_description_with_ai
import re
from app.validators import validate_images

logger = logging.getLogger(__name__)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def parse_clarification_to_questions(
    clarification: Optional[str],
    has_images: bool = True,
) -> Optional[List[dict]]:
    """Parse clarification string into structured questions.
    
    Limits to maximum 3 most important questions to avoid overwhelming users.
    """
    if not clarification:
        return None

    questions = []
    # Split by newlines or question marks followed by space
    lines = re.split(r'\?[\s\n]+|\n+', clarification)

    for i, line in enumerate(lines):
        line = line.strip()
        # Skip very short fragments and unhelpful questions
        if line and len(line) > 5:
            line_lower = line.lower()
            # Skip photo/image related questions only when users already uploaded images
            if has_images and ("photo" in line_lower or "image" in line_lower or "picture" in line_lower):
                continue
            # Skip redundant/obvious questions
            if "how many" in line_lower and ("affect" in line_lower or "light" in line_lower or "impact" in line_lower):
                continue
            
            questions.append({
                "id": f"q{len(questions)+1}",
                "question": line + ("?" if not line.endswith("?") else ""),
                "type": "text",
                "choices": None
            })
            
            # Limit to 3 most important questions
            if len(questions) >= 3:
                break

    return questions if questions else None


def transform_to_response(report: ReportInDB, base_url: str) -> ReportResponse:
    """Transform ReportInDB to ReportResponse with image objects."""
    images = None
    if report.report_images:
        images = [
            {"id": filename.split('_')[0], "url": f"{base_url}/uploads/{filename}"}
            for filename in report.report_images
        ]

    # Parse clarification into structured questions
    clarification_questions = parse_clarification_to_questions(
        report.clarification,
        has_images=bool(report.report_images),
    )
    events = list(report.events or []) if hasattr(report, "events") else None

    return ReportResponse(
        id=report.id,
        title=report.title,
        description=report.description,
        status=report.status,
        latitude=report.latitude,
        longitude=report.longitude,
        images=images,
        thread_id=report.thread_id,
        category=report.category,
        severity=report.severity,
        priority=report.priority,
        priority_score=report.priority_score,
        needs_clarification=report.needs_clarification,
        clarification=report.clarification,
        clarification_questions=clarification_questions,
        events=events,
        number_of_matches=report.number_of_matches,
        address=report.address,
        creation_time=report.creation_time,
        updated_at=report.updated_at,
    )

app = FastAPI(title="CityPulse API", version="1.0.0")

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Validate database connection and initialize AI assistant on startup.
    
    Fails fast if database is unreachable, preventing the app from
    starting in a broken state.
    """
    logger.info("Validating database connection...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection validated successfully")
    except Exception as exc:
        logger.error("Failed to connect to database on startup: %s", exc)
        raise RuntimeError(
            "Database connection failed. Cannot start application."
        ) from exc
    
    logger.info("Initializing Backboard AI assistant...")
    try:
        assistant_id = create_assistant()
        if assistant_id:
            logger.info("AI assistant initialized successfully: %s", assistant_id)
        else:
            logger.warning("AI assistant initialization failed - reports may not be processed correctly")
    except Exception as exc:
        logger.warning("Error during AI assistant initialization: %s", exc)

# CORS configuration - uses CORS_ORIGINS env var (comma-separated) or defaults for development
cors_origins_env = os.environ.get("CORS_ORIGINS", "")
if cors_origins_env:
    # Production: use explicit origins from environment
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    logger.info("CORS: Using configured origins: %s", cors_origins)
else:
    # Development: allow localhost and Docker internal network
    cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://frontend:3000"]
    logger.info("CORS: Using development defaults (localhost:3000, frontend:3000)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health")
def health():
    """Health check endpoint - required for Docker.
    Tries a trivial DB query; returns 503 if connection fails.
    """
    try:
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


@app.post("/reports", response_model=ReportResponse)
async def create_report(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    issue_images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
):
    """Create a new report."""
    if issue_images:
        validate_images(issue_images)
    saved_filenames = []
    for file in issue_images:
        contents = await file.read()
        filename = f"{uuid.uuid4()}_{file.filename}"

        # Save to local storage (or S3, etc.)
        with open(UPLOAD_DIR / filename, "wb") as f:
            f.write(contents)
        saved_filenames.append(filename)
        
        # Seek back to the start so the file can be read again
        await file.seek(0)
    
    input_report = Report(
        title=title,
        description=description,
        latitude=latitude,
        longitude=longitude,
        report_images=saved_filenames
    )

    report_id = uuid.uuid4()

    # Resolve human-readable address from coordinates so AI doesn't re-ask
    resolved_address = reverse_geocode(latitude, longitude)
    
    # Query for similar reports to pass count to AI
    similar_count = crud.get_similar_reports_count(
        db=db,
        category=None,  # Category not yet determined
        latitude=latitude,
        longitude=longitude,
        exclude_report_id=report_id
    )

    try:
        thread_id, creation_time, ai_response = run_backboard_ai(
            description=description,
            latitude=latitude,
            longitude=longitude,
            image_files=issue_images,
            number_of_matches=similar_count,
        )
        if thread_id is None or creation_time is None or ai_response == {}:
            logger.error("AI workflow returned an invalid response")
            raise HTTPException(status_code=500, detail="AI workflow failed")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in AI workflow")
        raise HTTPException(status_code=500, detail="AI workflow failed") from None

    try:
        report = crud.create_report(
            db=db,
            user_report=input_report,
            ai_response=ai_response,
            report_id=report_id,
            thread_id=thread_id,
            creation_time=creation_time,
            address=resolved_address,
        )
    except Exception:
        logger.exception("Failed to persist report")
        raise HTTPException(status_code=500, detail="Failed to create report")

    # Start background task to clean description (don't wait for completion)
    Thread(
        target=clean_description_with_ai,
        args=(report_id, description),
        daemon=True
    ).start()

    base_url = str(request.base_url).rstrip("/")
    return transform_to_response(report, base_url)

@app.post("/reports/{report_id}/followup", response_model=ReportResponse)
async def make_followup(
    request: Request,
    report_id: UUID,
    answers: ReportFollowup,
    db: Session = Depends(get_db)
):
    report = crud.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    clarification_answers = answers.followup or {}
    provided_description = clarification_answers.get("description")
    
    # Convert image filenames to full paths for AI workflow
    image_paths = []
    if report.report_images:
        for filename in report.report_images:
            full_path = UPLOAD_DIR / filename
            if full_path.exists():
                image_paths.append(str(full_path))
    
    # Query for similar reports to pass count to AI
    similar_count = crud.get_similar_reports_count(
        db=db,
        category=report.category,
        latitude=clarification_answers.get("latitude") or report.latitude,
        longitude=clarification_answers.get("longitude") or report.longitude,
        exclude_report_id=report_id
    )
    
    # Include the user's clarification answers in the message sent back to the AI
    questions = parse_clarification_to_questions(
        report.clarification,
        has_images=bool(report.report_images),
    )
    question_map = {q["id"]: q["question"] for q in questions or []}
    answer_lines = []
    for key, value in clarification_answers.items():
        if key == "description":
            # Avoid duplicating description in the answer context; it is handled separately
            continue
        if value is None:
            continue
        value_str = str(value).strip()
        if not value_str:
            continue
        question_text = question_map.get(key)
        if question_text:
            answer_lines.append(f"Q: {question_text} A: {value_str}")
        else:
            answer_lines.append(f"{key}: {value_str}")

    followup_description = provided_description or report.description
    if answer_lines:
        followup_description = followup_description + "\n\nUser clarification answers:\n" + "\n".join(answer_lines)

    # Extract follow-up fields for persistence and AI context
    followup_latitude = clarification_answers.get("latitude") or report.latitude
    followup_longitude = clarification_answers.get("longitude") or report.longitude
    followup_address = reverse_geocode(followup_latitude, followup_longitude)

    try:
        result = ai_followup(
            thread_id=report.thread_id,
            description=followup_description,
            latitude=followup_latitude,
            longitude=followup_longitude,
            image_paths=image_paths,
            number_of_matches=similar_count
        )
    except Exception:
        logger.exception("Failed to process followup")
        raise HTTPException(status_code=500, detail="AI followup failed") from None

    # Update report with AI response and follow-up data
    if result:
        report = crud.update_report_with_ai_response(
            db=db,
            report_id=report_id,
            ai_response=result,
            new_description=followup_description,
            new_latitude=followup_latitude,
            new_longitude=followup_longitude,
            number_of_matches=similar_count,
            new_address=followup_address
        )
        if not report:
            raise HTTPException(status_code=404, detail="Report not found after update")
    else:
        logger.warning("AI followup returned empty result for report %s", report_id)
        report = crud.get_report(db=db, report_id=report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

    base_url = str(request.base_url).rstrip("/")
    return transform_to_response(report, base_url)


@app.get("/reports", response_model=List[ReportResponse])
def list_reports(
    request: Request,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all reports with optional filtering."""
    reports = crud.get_reports(db=db, status_filter=status_filter, priority_filter=priority_filter, category_filter=category_filter)
    base_url = str(request.base_url).rstrip("/")
    return [transform_to_response(report, base_url) for report in reports]


@app.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(
    request: Request,
    report_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a single report by ID."""
    report = crud.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    base_url = str(request.base_url).rstrip("/")
    return transform_to_response(report, base_url)


# TODO: add authentication middleware and role check
@app.put("/reports/{report_id}", response_model=ReportResponse)
def update_report(
    request: Request,
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
    base_url = str(request.base_url).rstrip("/")
    return transform_to_response(report, base_url)


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
