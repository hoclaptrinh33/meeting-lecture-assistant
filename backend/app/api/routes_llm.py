"""API kích hoạt và kiểm tra tiến độ tác vụ hậu kỳ LLM (clean, summarize)."""
from typing import Literal
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.llm import (
    LlmRunDetailResponse,
    LlmTriggerResponse,
    SummarizeRequest,
)

router = APIRouter(prefix="/api/jobs", tags=["llm"])


@router.post("/{job_id}/llm/clean", response_model=LlmTriggerResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_clean(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Kích hoạt tác vụ làm sạch văn bản bằng LLM.
    TODO: Kiểm tra trạng thái job ready, tạo LlmRun task=clean và đẩy task run_llm vào hàng IO.
    """
    pass


@router.post("/{job_id}/llm/summarize", response_model=LlmTriggerResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_summarize(
    job_id: uuid.UUID,
    req: SummarizeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Kích hoạt tác vụ tóm tắt cuộc họp hoặc bài giảng bằng LLM.
    TODO: Kiểm tra trạng thái job ready, tạo LlmRun task=summarize và đẩy task run_llm vào hàng IO.
    """
    pass


@router.get("/{job_id}/llm/{task}", response_model=LlmRunDetailResponse)
def get_llm_run_status(
    job_id: uuid.UUID,
    task: Literal["clean", "summarize"],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy trạng thái và kết quả lần chạy mới nhất của tác vụ LLM.
    TODO: Lấy LlmRun mới nhất theo task và job_id.
    """
    pass
