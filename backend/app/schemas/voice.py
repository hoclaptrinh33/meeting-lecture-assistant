import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VoiceProfileResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    status: str
    duration_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class VoiceProfileCreateResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    status: str = "processing"
