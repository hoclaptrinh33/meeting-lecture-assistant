from typing import Literal
from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    format: Literal["md", "docx", "pdf", "srt", "vtt"]
    text: Literal["auto", "raw", "cleaned", "edited"] = "auto"
    include_speakers: bool = True
