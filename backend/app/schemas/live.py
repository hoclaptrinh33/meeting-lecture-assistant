import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LiveSessionCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    vocabulary: Optional[str] = Field(default=None, max_length=800)
    num_speakers: Optional[int] = Field(default=None, ge=1, le=20)


class LiveSessionCreateResponse(BaseModel):
    session_id: uuid.UUID
    status: str = "capturing"
    ws_ticket: str


class LiveSessionStopResponse(BaseModel):
    session_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    status: str = "stopping"


class LiveSessionDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    job_id: Optional[uuid.UUID] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True
