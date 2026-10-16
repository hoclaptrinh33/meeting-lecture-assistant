import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import SessionLocal, get_db
from app.core.exceptions import GpuBusyException, NotFoundException, UnauthorizedException
from app.core.security import generate_random_token, hash_token
from app.models import Job, LiveSession, User, WsTicket
from app.schemas.live import (
    LiveSessionCreateRequest,
    LiveSessionCreateResponse,
    LiveSessionDetailResponse,
    LiveSessionStopResponse,
)
from app.services.gpu_lock import GpuLock

router = APIRouter(prefix="/api/live", tags=["live"])


@router.post("/sessions", response_model=LiveSessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_live_session(
    req: LiveSessionCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session_id = uuid.uuid4()
    gpu_lock = GpuLock(owner_id=str(session_id))

    # Cố gắng lấy khóa GPU ngay lập tức
    if not gpu_lock.acquire():
        raise GpuBusyException()

    session = LiveSession(
        id=session_id,
        user_id=user.id,
        title=req.title.strip(),
        status="capturing",
        vocabulary=req.vocabulary,
        num_speakers=req.num_speakers,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(session)

    # Tạo ws_ticket ngắn hạn (60 giây) để kết nối WebSocket
    raw_ticket = generate_random_token()
    ticket_rec = WsTicket(
        token_hash=hash_token(raw_ticket),
        session_id=session_id,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=60),
    )
    db.add(ticket_rec)
    db.commit()

    return LiveSessionCreateResponse(
        session_id=session.id,
        status="capturing",
        ws_ticket=raw_ticket,
    )


@router.post("/sessions/{session_id}/stop", response_model=LiveSessionStopResponse)
def stop_live_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(LiveSession).filter(LiveSession.id == session_id, LiveSession.user_id == user.id).first()
    if not session:
        raise NotFoundException("Phiên nghe không tồn tại.")

    session.status = "stopping"
    session.ended_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()

    return LiveSessionStopResponse(
        session_id=session.id,
        job_id=session.job_id,
        status="stopping",
    )


@router.get("/sessions/{session_id}", response_model=LiveSessionDetailResponse)
def get_live_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = db.query(LiveSession).filter(LiveSession.id == session_id, LiveSession.user_id == user.id).first()
    if not session:
        raise NotFoundException("Phiên nghe không tồn tại.")

    return LiveSessionDetailResponse.model_validate(session)


@router.websocket("/ws/{session_id}")
async def websocket_live_pcm(websocket: WebSocket, session_id: uuid.UUID, ticket: str = Query(...)):
    """WebSocket nhận stream PCM 16kHz mono float32 từ browser cho PT2."""
    db = SessionLocal()
    try:
        token_hashed = hash_token(ticket)
        now = datetime.datetime.now(datetime.timezone.utc)
        ticket_rec = (
            db.query(WsTicket)
            .filter(WsTicket.token_hash == token_hashed, WsTicket.session_id == session_id, WsTicket.expires_at > now)
            .first()
        )
        if not ticket_rec:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Xóa ticket sau khi dùng
        db.delete(ticket_rec)
        db.commit()

        await websocket.accept()

        while True:
            # Nhận chunk nhị phân PCM float32
            data = await websocket.receive_bytes()
            if not data:
                break
    except WebSocketDisconnect:
        pass
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
    finally:
        db.close()
