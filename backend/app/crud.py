from sqlalchemy.orm import Session
from uuid import UUID

from app import models
from app.schemas import ReportCreate


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
    db.commit()
    db.refresh(report)
    return report


def get_reports(db: Session):
    return db.query(models.IssueTable).order_by(models.IssueTable.creationTime.desc()).all()


def get_report(db: Session, report_id: str):
    uid = _parse_uuid(report_id)
    if uid is None:
        return None
    return db.query(models.IssueTable).filter(models.IssueTable.id == uid).first()

#delete/update

