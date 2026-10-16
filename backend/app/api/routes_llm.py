import datetime
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import (
    InvalidStateException,
    LlmNotConfiguredException,
    NotFoundException,
)
from app.models import Job, LlmRun, User
from app.schemas.llm import (
    LlmRunDetailResponse,
    LlmTriggerResponse,
    SummarizeRequest,
)
from app.tasks.io_tasks import run_llm

router = APIRouter(prefix="/api/jobs", tags=["llm"])


def _check_running_llm(job_id: uuid.UUID, db: Session) -> None:
    running = db.query(LlmRun).filter(LlmRun.job_id == job_id, LlmRun.status == "running").first()
    if running:
        raise InvalidStateException("Một tác vụ LLM khác đang được thực thi trên job này.")


@router.post("/{job_id}/llm/clean", response_model=LlmTriggerResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_clean(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not settings.LLM_MODEL:
        raise LlmNotConfiguredException()

    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")
    if job.status != "ready":
        raise InvalidStateException("Job chưa sẵn sàng để thực hiện hậu kỳ.")

    _check_running_llm(job_id, db)

    run = LlmRun(
        id=uuid.uuid4(),
        job_id=job_id,
        task="clean",
        status="running",
        model_name=settings.LLM_MODEL,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(run)
    db.commit()

    run_llm.delay(str(run.id))

    return LlmTriggerResponse(run_id=run.id, status="running")


@router.post("/{job_id}/llm/summarize", response_model=LlmTriggerResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_summarize(
    job_id: uuid.UUID,
    req: SummarizeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not settings.LLM_MODEL:
        raise LlmNotConfiguredException()

    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")
    if job.status != "ready":
        raise InvalidStateException("Job chưa sẵn sàng để thực hiện tóm tắt.")

    _check_running_llm(job_id, db)

    run = LlmRun(
        id=uuid.uuid4(),
        job_id=job_id,
        task="summarize",
        template=req.template,
        status="running",
        model_name=settings.LLM_MODEL,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(run)
    db.commit()

    run_llm.delay(str(run.id))

    return LlmTriggerResponse(run_id=run.id, status="running")


@router.get("/{job_id}/llm/{task}", response_model=LlmRunDetailResponse)
def get_llm_run_status(
    job_id: uuid.UUID,
    task: Literal["clean", "summarize"],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    run = (
        db.query(LlmRun)
        .filter(LlmRun.job_id == job_id, LlmRun.task == task)
        .order_by(LlmRun.created_at.desc())
        .first()
    )
    if not run:
        raise NotFoundException("Chưa có lượt chạy LLM nào cho tác vụ này.")

    return LlmRunDetailResponse(
        run_id=run.id,
        task=run.task,
        status=run.status,
        template=run.template,
        model=run.model_name,
        result=run.result,
        error_code=run.error_code,
        error_message=run.error_message,
    )
