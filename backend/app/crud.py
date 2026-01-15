from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from datetime import datetime, timezone
from typing import Union, Optional
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
    creation_time: Union[str, datetime],
    address: Optional[str] = None,
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

    # Determine status based on whether AI needs clarification
    status = user_report.status
    if ai_response.get("needs_clarification"):
        status = "Waiting for user follow-up"

    report = models.IssueTable(
        id=coerced_report_id,
        title=user_report.title,
        description=user_report.description,
        status=status,
        latitude=user_report.latitude,
        longitude=user_report.longitude,
        address=address,
        report_images=user_report.report_images,
        thread_id=thread_id_str,
        category=ai_response.get("classification"),
        severity=ai_response.get("severity"),
        priority=ai_response.get("priority"),
        priority_score=ai_response.get("priority_score"),
        needs_clarification=ai_response.get("needs_clarification"),
        clarification=ai_response.get("clarification"),
        number_of_matches=ai_response.get("number_of_matches", 0),
        creation_time=coerced_creation_time,
    )
    db.add(report)
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    db.refresh(report)
    return report


def get_reports(
    db: Session,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    category_filter: Optional[str] = None
):
    query = db.query(models.IssueTable)

    if status_filter:
        query = query.filter(models.IssueTable.status == status_filter)
    if priority_filter:
        query = query.filter(models.IssueTable.priority == priority_filter)
    if category_filter:
        query = query.filter(models.IssueTable.category == category_filter)

    return query.order_by(models.IssueTable.creation_time.desc()).all()


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


def update_report_with_ai_response(
    db: Session,
    report_id: Union[str, UUID],
    ai_response: dict,
    new_description: Optional[str] = None,
    new_latitude: Optional[float] = None,
    new_longitude: Optional[float] = None,
    number_of_matches: Optional[int] = None,
    new_address: Optional[str] = None,
) -> Optional[models.IssueTable]:
    """Update a report with AI-enriched fields from follow-up.

    Args:
        db: Database session
        report_id: Report UUID
        ai_response: AI response dictionary with enriched fields
        new_description: Updated description from follow-up (if provided)
        new_latitude: Updated latitude from follow-up (if provided)
        new_longitude: Updated longitude from follow-up (if provided)
        number_of_matches: Backend-calculated similar reports count (fallback if AI doesn't return it)
    """
    report = get_report(db, report_id)
    if report is None:
        return None

    # Update user-provided fields from follow-up
    if new_description is not None:
        report.description = new_description
    if new_latitude is not None:
        report.latitude = new_latitude
    if new_longitude is not None:
        report.longitude = new_longitude
    if new_address is not None:
        report.address = new_address

    # Update AI-enriched fields from response
    if "classification" in ai_response:
        report.category = ai_response["classification"]
    if "severity" in ai_response:
        report.severity = ai_response["severity"]
    if "priority" in ai_response:
        report.priority = ai_response["priority"]
    if "priority_score" in ai_response:
        report.priority_score = ai_response["priority_score"]
    if "needs_clarification" in ai_response:
        report.needs_clarification = ai_response["needs_clarification"]
    if "clarification" in ai_response:
        report.clarification = ai_response["clarification"]

    # Use AI's number_of_matches if provided, otherwise use backend-calculated value
    if "number_of_matches" in ai_response:
        report.number_of_matches = ai_response["number_of_matches"]
    elif number_of_matches is not None:
        report.number_of_matches = number_of_matches

    # Keep status aligned with AI clarification state
    if ai_response.get("needs_clarification") is True:
        report.status = "Waiting for user follow-up"
    elif ai_response.get("needs_clarification") is False:
        if report.status in (None, "", "Waiting for user follow-up"):
            report.status = "New"

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(report)
    return report


def get_similar_reports_count(
    db: Session,
    category: Optional[str],
    latitude: Optional[float],
    longitude: Optional[float],
    exclude_report_id: Optional[Union[str, UUID]] = None,
    lat_tolerance: float = 0.01,  # ~1km
    lon_tolerance: float = 0.01
) -> int:
    """Count similar reports based on category and nearby location.
    
    Args:
        db: Database session
        category: Category/classification of the report
        latitude: Report latitude
        longitude: Report longitude
        exclude_report_id: Report ID to exclude from count (current report)
        lat_tolerance: Latitude bounding box tolerance
        lon_tolerance: Longitude bounding box tolerance
    
    Returns:
        Count of similar reports
    """
    # If we have no category and no coordinates, avoid counting everything
    if not category and (latitude is None or longitude is None):
        return 0

    query = db.query(models.IssueTable)
    
    # Filter by category if provided
    if category:
        query = query.filter(models.IssueTable.category == category)
    
    # Filter by nearby location if coordinates provided
    if latitude is not None and longitude is not None:
        query = query.filter(
            models.IssueTable.latitude.between(latitude - lat_tolerance, latitude + lat_tolerance),
            models.IssueTable.longitude.between(longitude - lon_tolerance, longitude + lon_tolerance)
        )
    
    # Exclude the current report
    if exclude_report_id:
        coerced_id = _coerce_uuid(exclude_report_id)
        if coerced_id:
            query = query.filter(models.IssueTable.id != coerced_id)
    
    return query.count()


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
