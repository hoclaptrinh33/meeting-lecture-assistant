from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class JobEventOut(BaseModel):
    seq: int
    event: str
    data: Dict[str, Any]


class StageChangedPayload(BaseModel):
    stage: str
    percent: Optional[int] = None


class SegmentWordPayload(BaseModel):
    text: str
    start_ms: int
    end_ms: int


class SegmentAddedPayload(BaseModel):
    pass_number: int
    position: int
    start_ms: int
    end_ms: int
    text_raw: str
    words: List[SegmentWordPayload] = []


class WordsUpdatedPayload(BaseModel):
    pass_number: int
    position: int
    words: List[Dict[str, Any]]


class SpeakerAssignedPayload(BaseModel):
    pass_number: int
    position: int
    speaker_label: str


class WarningPayload(BaseModel):
    code: str
    message: str


class FinishedPayload(BaseModel):
    duration_ms: int
    status: str = "ready"


class ErrorPayload(BaseModel):
    code: str
    message: str
