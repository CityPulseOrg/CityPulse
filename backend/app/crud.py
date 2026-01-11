from sqlalchemy.orm import Session
from uuid import UUID
from typing import Union, Optional
from app import models
from app.schemas import *

# -------------------------------
# CREATE

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

# -------------------------------
# CREATE

def create_report(
        db: Session,
        user_report: Report,
        ai_response: dict,
        report_id: Union[str, UUID],
        thread_id: Union[str, UUID],
        creation_time: str
) -> models.IssueTable:
    # Coerce report_id to UUID (model column is UUID)
    coerced_report_id = _coerce_uuid(report_id)
    if coerced_report_id is None:
        raise ValueError(f"Invalid report_id: {report_id}")

    # Convert thread_id to string (model column is String)
    thread_id_str = str(thread_id) if thread_id is not None else None

    report = models.IssueTable(
        id=coerced_report_id,
        title=user_report.title,
        description=user_report.description,
        address=user_report.address,
        city=user_report.city,
        latitude=user_report.latitude,
        longitude=user_report.longitude,
        threadId=thread_id_str,
        category=ai_response.get("classification"),
        severity=ai_response.get("severity"),
        priority=ai_response.get("priority"),
        priority_score=ai_response.get("priority_score"),
        needs_clarification=ai_response.get("needs_clarification"),
        clarification=ai_response.get("clarification"),
        #TODO: Add nbOfMatches here once the AI is programmed to get the number of matches
        creationTime=creation_time,
    )
    db.add(report)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(report)
    return report


#-----------------
# READ

def get_reports(db: Session):
    return db.query(models.IssueTable).order_by(models.IssueTable.creationTime.desc()).all()


#TODO: Make sure that the coerce_uuid function is necessary
def get_report(db: Session, report_id: Union[str, UUID]) -> Optional[models.IssueTable]:
    uuid = _coerce_uuid(report_id)
    if uuid is None:
        return None
    return db.query(models.IssueTable).filter(models.IssueTable.id == uuid).first()

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
    except Exception:
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
    except Exception:
        db.rollback()
        raise

    return True

