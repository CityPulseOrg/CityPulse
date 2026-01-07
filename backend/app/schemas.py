"""
CityPulse Pydantic Schemas
Request/response models for API validation.

TODO: To be implemented by Zak
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Report(BaseModel):
    title: str
    description: str
    address: str
    city: str
    status: str = "New"                   #TODO: Verify if need to create another class for status update
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ReportInDB(Report):
    id: int
    status: str = "New"
    thread_id: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    nbOfMatches: int = 0
    creationTime: datetime

    class Config:
        orn_mode = True

class ReportEvent(BaseModel):
    eventType: str
    payload: Optional[str] = None

class ReportEventInDB(ReportEvent):
    id: int
    reportId: int
    creationTime: datetime

    class Config:
        orn_mode = True

class ReportEventList(ReportInDB):
    events: list[ReportEventInDB] = []

