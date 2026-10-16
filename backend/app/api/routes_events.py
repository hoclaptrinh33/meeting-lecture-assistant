"""API Server-Sent Events (SSE) đẩy tiến độ và kết quả nhận dạng theo thời gian thực."""
import uuid
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User

router = APIRouter(prefix="/api/jobs", tags=["events"])


@router.get("/{job_id}/events")
async def stream_job_events(
    job_id: uuid.UUID,
    from_seq: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Server-Sent Events (SSE) đẩy tiến độ nhận dạng.
    TODO: Đọc các event cũ từ job_events (seq > from_seq) và lắng nghe kênh Redis Pub/Sub job:{job_id}:events.
    """
    pass
