from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
<<<<<<< Updated upstream
from datetime import datetime, timezone
from typing import Union, Optional
=======
from typing import Optional

>>>>>>> Stashed changes
from app import models
from app.schemas import Report

def _parse_uuid(value: str) -> Optional[UUID]:
    try:
        return UUID(value)
    except Exception:
        return None

def _coerce_uuid(value: Union[str, UUID]) -> Optional[UUID]:
    """Accept UUID or str; return UUID or None if invalid."""
    if isinstance(value, UUID):
        return value
    return _parse_uuid(value)

def _coerce_datetime(value: Union[str, datetime]) -> Optional[datetime]:
    """Accept datetime or ISO string; return timezone-aware datetime or None if invalid."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None

# -------------------------------
# CREATE

def create_report(
        db: Session,
        user_report: Report,
        ai_response: dict,
        report_id: Union[str, UUID],
        thread_id: Union[str, UUID],
        creation_time: Union[str, datetime]
) -> models.IssueTable:
    # Coerce report_id to UUID (model column is UUID)
    coerced_report_id = _coerce_uuid(report_id)
    if coerced_report_id is None:
        raise ValueError(f"Invalid report_id: {report_id}")

    # Convert thread_id to string (model column is String)
    thread_id_str = str(thread_id) if thread_id is not None else None

    # Coerce creation_time to timezone-aware datetime
    coerced_creation_time = _coerce_datetime(creation_time)
    if coerced_creation_time is None:
        raise ValueError(f"Invalid creation_time: {creation_time}")

<<<<<<< Updated upstream
    report = models.IssueTable(
        id=coerced_report_id,
        title=user_report.title,
        description=user_report.description,
        address=user_report.address,
        city=user_report.city,
        status=user_report.status,
        latitude=user_report.latitude,
        longitude=user_report.longitude,
        thread_id=thread_id_str,
        category=ai_response.get("classification"),
        severity=ai_response.get("severity"),
        priority=ai_response.get("priority"),
        priority_score=ai_response.get("priority_score"),
        needs_clarification=ai_response.get("needs_clarification"),
        clarification=ai_response.get("clarification"),
        #TODO: Add nbOfMatches here once the AI is programmed to get the number of matches
        creation_time=coerced_creation_time,
=======
def create_report_with_ai(
    db: Session,
    userReport: Report,
    aiResponse: dict,
    threadId: str,
    priority: str,
    risk: str,
    category: Optional[str] = None
) -> models.IssueTable:
    """Create a report with AI-enriched data including priority and risk assessment."""
    report = models.IssueTable(
        title=userReport.title,
        description=userReport.description,
        address="",  # TODO: Add address field to Report schema
        city="",     # TODO: Add city field to Report schema
        status="open",
        latitude=userReport.latitude,
        longitude=userReport.longitude,
        threadId=threadId,
        category=category,
        priority=priority,
        severity=risk,  # Using severity field for risk level
        nbOfMatches=0
>>>>>>> Stashed changes
    )
    db.add(report)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    db.refresh(report)
    return report


<<<<<<< Updated upstream
#-----------------
# READ

def get_reports(db: Session, status_filter: Optional[str] = None):
    query = db.query(models.IssueTable)
    if status_filter:
        query = query.filter(models.IssueTable.status == status_filter)
    return query.order_by(models.IssueTable.creation_time.desc()).all()
=======
def get_reports(
    db: Session,
    statusFilter: Optional[str] = None,
    priorityFilter: Optional[str] = None,
    categoryFilter: Optional[str] = None
):
    """Get reports with optional filtering."""
    query = db.query(models.IssueTable)

    if statusFilter:
        query = query.filter(models.IssueTable.status == statusFilter)
    if priorityFilter:
        query = query.filter(models.IssueTable.priority == priorityFilter)
    if categoryFilter:
        query = query.filter(models.IssueTable.category == categoryFilter)

    return query.order_by(models.IssueTable.creationTime.desc()).all()
>>>>>>> Stashed changes


def get_report(db: Session, report_id: Union[str, UUID]) -> Optional[models.IssueTable]:
    coerced_id = _coerce_uuid(report_id)
    if coerced_id is None:
        return None
    return db.query(models.IssueTable).filter(models.IssueTable.id == coerced_id).first()

# -------------------------
# UPDATE

def update_report(
    db: Session,
    report_id: Union[str, UUID],
    new_title: Optional[str] = None,
    new_description: Optional[str] = None,
    new_status: Optional[str] = None,
    new_address: Optional[str] = None,
    new_city: Optional[str] = None,
    new_latitude: Optional[float] = None,
    new_longitude: Optional[float] = None
) -> Optional[models.IssueTable]:
    report = get_report(db, report_id)
    if report is None:
        return None

    updates = {
        "title": new_title,
        "description": new_description,
        "status": new_status,
        "address": new_address,
        "city": new_city,
        "latitude": new_latitude,
        "longitude": new_longitude,
    }

    for field, value in updates.items():
        if value is not None:
            setattr(report, field, value)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(report)
    return report


# -------------------------
# DELETE

def delete_report(db: Session, report_id: Union[str, UUID]) -> bool:
    report = get_report(db, report_id)
    if report is None:
        return False

    db.delete(report)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return True

