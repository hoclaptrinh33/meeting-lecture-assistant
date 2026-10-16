"""API quản lý công việc (Jobs), transcript, người nói, highlights, action items và audio."""
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.jobs import (
    ActionItemDto,
    CreateActionItemRequest,
    CreateHighlightRequest,
    HighlightItem,
    JobCreateResponse,
    JobDetailResponse,
    JobListResponse,
    MediaTokenResponse,
    PatchActionItemRequest,
    PatchSegmentRequest,
    PatchSpeakerRequest,
    TranscriptResponse,
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    vocabulary: Optional[str] = Form(None),
    num_speakers: Optional[int] = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tải lên file âm thanh/video và tạo job nhận dạng.
    TODO: Lưu file, tạo bản ghi Job và đẩy task transcribe_upload vào hàng GPU.
    """
    pass


@router.get("", response_model=JobListResponse)
def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy danh sách các job của người dùng với phân trang cursor.
    TODO: Lấy danh sách job sắp xếp theo created_at giảm dần.
    """
    pass


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_detail(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy chi tiết trạng thái và thông tin của một job.
    TODO: Lấy job theo ID và xác thực quyền sở hữu.
    """
    pass


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa job và dữ liệu âm thanh liên quan.
    TODO: Xóa file audio và bản ghi job khỏi DB.
    """
    pass


@router.post("/{job_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Hủy một job đang chờ hoặc đang chạy.
    TODO: Đổi trạng thái job thành cancelled.
    """
    pass


@router.get("/{job_id}/transcript", response_model=TranscriptResponse)
def get_transcript(
    job_id: uuid.UUID,
    pass_number: int = Query(2, alias="pass"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy toàn bộ transcript gồm các câu, từ, speaker, highlights và action items.
    TODO: Truy vấn segments, words, aliases, highlights, action_items.
    """
    pass


@router.patch("/{job_id}/segments/{position}")
def patch_segment(
    job_id: uuid.UUID,
    position: int,
    req: PatchSegmentRequest,
    pass_number: int = Query(2, alias="pass"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sửa nội dung văn bản của một câu (text_edited).
    TODO: Cập nhật text_edited cho segment tại position.
    """
    pass


@router.patch("/{job_id}/speakers/{speaker_label}")
def patch_speaker(
    job_id: uuid.UUID,
    speaker_label: str,
    req: PatchSpeakerRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Đổi tên hiển thị của người nói.
    TODO: Cập nhật speaker_aliases cho job.
    """
    pass


@router.post("/{job_id}/highlights", status_code=status.HTTP_201_CREATED)
def create_highlight(
    job_id: uuid.UUID,
    req: CreateHighlightRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Đánh dấu đoạn trích dẫn quan trọng trong transcript.
    TODO: Lưu bản ghi Highlight.
    """
    pass


@router.delete("/{job_id}/highlights/{highlight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_highlight(
    job_id: uuid.UUID,
    highlight_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa đoạn đánh dấu.
    TODO: Xóa bản ghi Highlight.
    """
    pass


@router.post("/{job_id}/action-items", status_code=status.HTTP_201_CREATED)
def create_action_item(
    job_id: uuid.UUID,
    req: CreateActionItemRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tạo việc cần làm thủ công gắn với mốc thời gian.
    TODO: Lưu bản ghi ActionItem.
    """
    pass


@router.patch("/{job_id}/action-items/{item_id}")
def update_action_item(
    job_id: uuid.UUID,
    item_id: uuid.UUID,
    req: PatchActionItemRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cập nhật thông tin việc cần làm.
    TODO: Cập nhật task, owner, deadline.
    """
    pass


@router.delete("/{job_id}/action-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action_item(
    job_id: uuid.UUID,
    item_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa việc cần làm.
    TODO: Xóa bản ghi ActionItem.
    """
    pass


@router.post("/{job_id}/media-token", response_model=MediaTokenResponse)
def create_media_token(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tạo token media ngắn hạn để stream audio.
    TODO: Tạo token ngẫu nhiên và lưu hash vào media_tokens.
    """
    pass


@router.get("/{job_id}/audio")
def stream_audio(
    job_id: uuid.UUID,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    """Phát luồng file âm thanh Opus cho trình duyệt.
    TODO: Kiểm tra media token và trả về FileResponse.
    """
    pass
