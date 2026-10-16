import json
import uuid
from typing import AsyncGenerator, Optional
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.core.redis import subscribe_events
from app.models import Job, JobEvent, User

router = APIRouter(prefix="/api/jobs", tags=["events"])


@router.get("/{job_id}/events")
async def stream_job_events(
    job_id: uuid.UUID,
    from_seq: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Server-Sent Events (SSE) đẩy tiến độ và kết quả nhận dạng theo thời gian thực."""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    # 1. Lấy các sự kiện cũ đã có trong DB
    past_events = (
        db.query(JobEvent)
        .filter(JobEvent.job_id == job_id, JobEvent.seq > from_seq)
        .order_by(JobEvent.seq.asc())
        .all()
    )

    async def event_generator() -> AsyncGenerator[str, None]:
        last_seq = from_seq
        for ev in past_events:
            last_seq = ev.seq
            yield f"id: {ev.seq}\nevent: {ev.event_type}\ndata: {json.dumps(ev.payload, ensure_ascii=False)}\n\n"
            if ev.event_type in ("finished", "error"):
                return

        # 2. Tiếp tục bám Redis Pub/Sub để lắng nghe sự kiện mới
        channel = f"job:{str(job_id)}:events"
        async for message in subscribe_events(channel):
            try:
                data = json.loads(message)
                seq = data.get("seq", last_seq + 1)
                event_type = data.get("event", "message")
                payload = data.get("data", {})

                if seq > last_seq:
                    last_seq = seq
                    yield f"id: {seq}\nevent: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

                if event_type in ("finished", "error"):
                    break
            except Exception:
                continue

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
