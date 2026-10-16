import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JobCreateResponse(BaseModel):
    job_id: uuid.UUID
    status: str = "queued"


class WarningItem(BaseModel):
    code: str
    message: str


class JobSummary(BaseModel):
    id: uuid.UUID
    title: str
    source: str
    status: str
    duration_ms: Optional[int] = None
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    items: List[JobSummary]
    next_cursor: Optional[str] = None


class JobDetailResponse(BaseModel):
    id: uuid.UUID
    title: str
    source: str
    status: str
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[WarningItem] = Field(default_factory=list)
    audio_url: Optional[str] = None
    duration_ms: Optional[int] = None
    vocabulary: Optional[str] = None
    num_speakers: Optional[int] = None
    diarization_device: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WordItem(BaseModel):
    position: int
    text: str
    start_ms: int
    end_ms: int
    speaker_label: Optional[str] = None

    class Config:
        from_attributes = True


class SegmentItem(BaseModel):
    id: uuid.UUID
    pass_number: int = Field(alias="pass")
    position: int
    start_ms: int
    end_ms: int
    text_raw: str
    text_cleaned: Optional[str] = None
    text_edited: Optional[str] = None
    speaker_label: Optional[str] = None
    words: List[WordItem] = Field(default_factory=list)

    class Config:
        from_attributes = True
        populate_by_name = True


class SpeakerAliasItem(BaseModel):
    speaker_label: str
    display_name: str
    source: str

    class Config:
        from_attributes = True


class HighlightItem(BaseModel):
    id: uuid.UUID
    segment_id: uuid.UUID
    quote: str
    start_ms: int
    end_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class ActionItemDto(BaseModel):
    id: uuid.UUID
    segment_id: Optional[uuid.UUID] = None
    start_ms: Optional[int] = None
    owner: str = ""
    task: str
    deadline: str = ""
    source: str = "manual"
    created_at: datetime

    class Config:
        from_attributes = True


class TranscriptResponse(BaseModel):
    segments: List[SegmentItem]
    speakers: List[SpeakerAliasItem]
    highlights: List[HighlightItem]
    action_items: List[ActionItemDto]


class PatchSegmentRequest(BaseModel):
    text_edited: str


class PatchSpeakerRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=100)


class CreateHighlightRequest(BaseModel):
    segment_id: uuid.UUID
    quote: str
    start_ms: int
    end_ms: int


class CreateActionItemRequest(BaseModel):
    task: str = Field(min_length=1)
    owner: Optional[str] = ""
    deadline: Optional[str] = ""
    start_ms: Optional[int] = None
    segment_id: Optional[uuid.UUID] = None


class PatchActionItemRequest(BaseModel):
    task: Optional[str] = None
    owner: Optional[str] = None
    deadline: Optional[str] = None


class MediaTokenResponse(BaseModel):
    token: str
    expires_in: int = 3600
