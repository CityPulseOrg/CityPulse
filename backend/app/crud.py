from sqlalchemy.orm import Session
from uuid import UUID
from typing import Union
from app import models
from app.schemas import ReportCreate

# -------------------------------
# CREATE

def _parse_uuid(value: str):
    try:
        return UUID(value)
    except Exception:
        return None


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


def get_report(db: Session, report_id: Union[str, UUID]):
    uid = _parse_uuid(report_id)
    if uid is None:
        return None
    return db.query(models.IssueTable).filter(models.IssueTable.id == uid).first()


# -------------------------
# UPDATE

def update_report(
    db: Session,
    report_id: str,
    new_title: str | None = None,
    new_description: str | None = None,
    new_status: str | None = None,
):
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

def delete_report(db: Session, report_id: UUID) -> bool:
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

