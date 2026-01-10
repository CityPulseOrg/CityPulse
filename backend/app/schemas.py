"""
CityPulse Pydantic Schemas
Request/response models for API validation.

TODO: To be implemented by Zak
"""
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID

#TODO: Verify if need to create another class for status update (note de Zak)
class Report(BaseModel):
    title: str
    description: str
    address: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ReportStatusUpdate(BaseModel):
    status: str

class ReportInDB(Report):
    id: UUID
    status: str = "New"
    threadId: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    nbOfMatches: int = 0
    creationTime: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportEvent(BaseModel):
    eventType: str
    payload: Optional[str] = None

class ReportEventInDB(ReportEvent):
    id: UUID
    reportId: UUID
    creationTime: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportEventList(ReportInDB):
    events: List[ReportEventInDB] = []


# ---- Aliases for Issue-based API (CityPulse v1) ----

class ReportCreate(Report):
    pass


class IssueOut(ReportInDB):
    pass





