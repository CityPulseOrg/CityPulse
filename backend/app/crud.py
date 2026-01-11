from sqlalchemy.orm import Session
from uuid import UUID

from app import models
from app.schemas import *


def _parse_uuid(value: str):
    try:
        return UUID(value)
    except Exception:
        return None


def create_report(
        db: Session,
        user_report: Report,
        ai_response: dict,
        report_id: UUID,
        thread_id: UUID,
        creation_time: str
) -> models.IssueTable:
    report = models.IssueTable(
        id=report_id,
        title=user_report.title,
        description=user_report.description,
        address=user_report.address,
        city=user_report.city,
        latitude=user_report.latitude,
        longitude=user_report.longitude,
        threadId=thread_id,
        category=ai_response.get("classification"),
        severity=ai_response.get("severity"),
        priority=ai_response.get("priority"),
        priority_score=ai_response.get("priority_score"),
        needs_clarification=ai_response.get("needs_clarification")
        clarification=ai_response.get("clarification")
        #TODO: Add nbOfmtaches here once the AI is programmed to get the number of matches
        creationTime=creation_time,
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

