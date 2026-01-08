from sqlalchemy.orm import Session
from app import models


def create_issue(db: Session, raw_text: str) -> models.Issue:
    issue = models.Issue(raw_text=raw_text, status="open")
    db.add(issue) 
    db.commit()
    db.refresh(issue) 
    return issue


def get_issues(db: Session) -> list[models.Issue]:
    return db.query(models.Issue).order_by(models.Issue.created_at.desc()).all()


def get_issue(db: Session, issue_id) -> models.Issue | None:
    return db.query(models.Issue).filter(models.Issue.id == issue_id).first()
