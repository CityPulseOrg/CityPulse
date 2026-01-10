from sqlalchemy.orm import Session
from uuid import UUID
from typing import Union, Optional
from app import models
from app.schemas import ReportCreate

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

def create_report(db: Session, payload: ReportCreate) -> models.IssueTable:
    report = models.IssueTable(
        title=payload.title,
        description=payload.description,
        address=payload.address,
        city=payload.city,
        status=payload.status,
        latitude=payload.latitude,
        longitude=payload.longitude,
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


def get_report(db: Session, report_id: Union[str, UUID]) -> Optional[models.IssueTable]:
    uid = _coerce_uuid(report_id)
    if uid is None:
        return None
    return db.query(models.IssueTable).filter(models.IssueTable.id == uid).first()

# -------------------------
# UPDATE

def update_report(
    db: Session,
    report_id: Union[str, UUID],
    new_title: Optional[str] = None,
    new_description: Optional[str] = None,
    new_status: Optional[str] = None,) -> Optional[models.IssueTable]:
    report = get_report(db, report_id)
    if report is None:
        return None

    updates = {
        "title": new_title,
        "description": new_description,
        "status": new_status,
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

