"""
CityPulse Database Models
SQLAlchemy models for the civic issue reporting system.

TODO: To be implemented by Bala/Zak
"""
import uuid
from datetime import datetime, timezone 

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class IssueTable(Base):
    __tablename__ = "issues"
    
    #TODO 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core user report fields (match schemas.Report / ReportInDB)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)

    status = Column(String, nullable=False, default="New")

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # AI-enriched fields
    threadId = Column(String, nullable=True)     
    category = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    nbOfMatches = Column(Integer, nullable=False, default=0)

    creationTime = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    events = relationship("IssueEventTable", back_populates="issue", cascade="all, delete-orphan")


class IssueEventTable(Base):
    __tablename__ = "issue_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reportId = Column(UUID(as_uuid=True), ForeignKey("issues.id"), nullable=False)

    eventType = Column(String, nullable=False)
    payload = Column(Text, nullable=True)

    creationTime = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    issue = relationship("IssueTable", back_populates="events")



