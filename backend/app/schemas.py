"""
CityPulse Pydantic Schemas
Request/response models for API validation.

"""
from enum import Enum
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class ClassificationEnum(str, Enum):
    POTHOLE = "pothole"
    BROKEN_STREETLIGHT = "broken_streetlight"
    BROKEN_STREET_SIGN = "broken_street_sign"
    EXCESSIVE_DUMPING = "excessive_dumping"
    ILLEGAL_GRAFFITI = "illegal_graffiti"
    VANDALISM = "vandalism"
    OVERGROWN_GRASS = "overgrown_grass"
    UNPLOWED_AREA = "unplowed_area"
    ICY_STREET = "icy_street"
    ICY_SIDEWALK = "icy_sidewalk"
    MALFUNCTIONING_WATERFOUNTAIN = "malfunctioning_waterfountain"
    OTHER = "other"


class SeverityEnum(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class PriorityEnum(str, Enum):
    NOT_URGENT = "not_urgent"
    URGENT = "urgent"
    VERY_URGENT = "very_urgent"


class ReportStatus(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    WAITING = "Waiting for user follow-up"


# TODO: Verify if we need a separate status-update-only schema
class Report(BaseModel):
    title: str
    description: str
    address: str
    city: str
    status: ReportStatus = ReportStatus.NEW
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ReportStatusUpdate(BaseModel):
    status: ReportStatus

class ReportUpdate(BaseModel):
    report_id: UUID
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ReportStatus] = None

class ReportInDB(Report):
    id: UUID
    threadId: Optional[str] = None
    category: Optional[ClassificationEnum] = None
    severity: Optional[SeverityEnum] = None
    priority: Optional[PriorityEnum] = None
    nbOfMatches: int = 0
    creationTime: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

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





