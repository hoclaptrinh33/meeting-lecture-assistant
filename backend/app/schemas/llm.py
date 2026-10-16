import uuid
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    template: Literal["meeting", "lecture"]


class LlmTriggerResponse(BaseModel):
    run_id: uuid.UUID
    status: str = "running"


class OpenIssueItem(BaseModel):
    timestamp: str
    text: str


class DecisionItem(BaseModel):
    timestamp: str
    text: str


class LlmActionItem(BaseModel):
    timestamp: str
    owner: str
    task: str
    deadline: str


class MeetingSummaryResult(BaseModel):
    objective: str
    open_issues: List[OpenIssueItem] = []
    decisions: List[DecisionItem] = []
    actions: List[LlmActionItem] = []


class ConceptItem(BaseModel):
    timestamp: str
    term: str
    explanation: str


class ExampleItem(BaseModel):
    timestamp: str
    text: str


class ExamNoteItem(BaseModel):
    timestamp: str
    text: str


class LectureSummaryResult(BaseModel):
    overview: str
    concepts: List[ConceptItem] = []
    examples: List[ExampleItem] = []
    exam_notes: List[ExamNoteItem] = []


class LlmRunDetailResponse(BaseModel):
    run_id: uuid.UUID
    task: Literal["clean", "summarize"]
    status: Literal["running", "done", "failed"]
    template: Optional[Literal["meeting", "lecture"]] = None
    model: Optional[str] = None
    result: Optional[Any] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
