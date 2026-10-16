"""API phiên nghe trực tiếp (PT2) và WebSocket truyền âm thanh PCM."""
import uuid

from fastapi import APIRouter, Depends, Query, WebSocket, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.live import (
    LiveSessionCreateRequest,
    LiveSessionCreateResponse,
    LiveSessionDetailResponse,
    LiveSessionStopResponse,
)

router = APIRouter(prefix="/api/live", tags=["live"])


@router.post("/sessions", response_model=LiveSessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_live_session(
    req: LiveSessionCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mở phiên nghe trực tiếp mới và cấp ticket WebSocket.
    TODO: Kiểm tra GPU lock (nếu bận trả 409), tạo LiveSession và tạo ws_ticket.
    """
    pass


@router.post("/sessions/{session_id}/stop", response_model=LiveSessionStopResponse)
def stop_live_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dừng phiên nghe trực tiếp và bắt đầu chạy pass 2 tổng hợp.
    TODO: Chuyển trạng thái session sang stopping và kích hoạt task pass 2.
    """
    pass


@router.get("/sessions/{session_id}", response_model=LiveSessionDetailResponse)
def get_live_session(
    session_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy thông tin chi tiết phiên nghe.
    TODO: Truy vấn LiveSession theo ID.
    """
    pass


@router.websocket("/ws/{session_id}")
async def websocket_live_pcm(websocket: WebSocket, session_id: uuid.UUID, ticket: str = Query(...)):
    """WebSocket nhận stream PCM 16kHz mono float32 từ browser cho PT2.
    TODO: Xác thực ws_ticket, nhận các buffer float32 nhị phân và đẩy vào hàng xử lý nháp.
    """
    pass
