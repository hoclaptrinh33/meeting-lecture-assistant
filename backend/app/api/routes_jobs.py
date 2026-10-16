import datetime
import os
from pathlib import Path
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import (
    FileTooLargeException,
    InvalidStateException,
    NotFoundException,
    UnauthorizedException,
    UnsupportedMediaException,
    ValidationException,
)
from app.core.security import generate_random_token, hash_token
from app.models import (
    ActionItem,
    Highlight,
    Job,
    MediaToken,
    Segment,
    SpeakerAlias,
    User,
    Word,
)
from app.schemas.jobs import (
    ActionItemDto,
    CreateActionItemRequest,
    CreateHighlightRequest,
    HighlightItem,
    JobCreateResponse,
    JobDetailResponse,
    JobListResponse,
    JobSummary,
    MediaTokenResponse,
    PatchActionItemRequest,
    PatchSegmentRequest,
    PatchSpeakerRequest,
    SegmentItem,
    SpeakerAliasItem,
    TranscriptResponse,
    WordItem,
)
from app.tasks.gpu_tasks import transcribe_upload

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

ALLOWED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".ogg", ".opus", ".flac",
    ".mp4", ".mkv", ".webm", ".mov",
}


@router.post("", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    vocabulary: Optional[str] = Form(None),
    num_speakers: Optional[int] = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedMediaException(f"Định dạng {ext} không được hỗ trợ.")

    job_title = (title or file.filename or "Ghi âm mới")[:200]
    job_id = uuid.uuid4()

    # Lưu file tạm thời
    data_dir = Path(settings.DATA_DIR) / "tmp"
    data_dir.mkdir(parents=True, exist_ok=True)
    raw_path = data_dir / f"{job_id}_raw{ext}"

    content = await file.read()
    if len(content) > settings.MAX_ORIGINAL_BYTES:
        raise FileTooLargeException("Kích thước file vượt quá 500 MB.")

    with open(raw_path, "wb") as f:
        f.write(content)

    job = Job(
        id=job_id,
        user_id=user.id,
        title=job_title,
        source="upload",
        status="queued",
        audio_path=str(raw_path),
        vocabulary=vocabulary[:800] if vocabulary else None,
        num_speakers=num_speakers if (num_speakers and 1 <= num_speakers <= 20) else None,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(job)
    db.commit()

    # Đẩy tác vụ vào hàng đợi GPU Celery
    transcribe_upload.delay(str(job_id))

    return JobCreateResponse(job_id=job.id, status=job.status)


@router.get("", response_model=JobListResponse)
def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Job).filter(Job.user_id == user.id).order_by(Job.created_at.desc())
    if cursor:
        try:
            cursor_dt = datetime.datetime.fromisoformat(cursor)
            query = query.filter(Job.created_at < cursor_dt)
        except ValueError:
            pass

    jobs = query.limit(limit + 1).all()
    has_next = len(jobs) > limit
    items = jobs[:limit]
    next_cursor = items[-1].created_at.isoformat() if has_next and items else None

    return JobListResponse(
        items=[JobSummary.model_validate(j) for j in items],
        next_cursor=next_cursor,
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job_detail(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")
    return JobDetailResponse.model_validate(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    # Xóa file audio
    if job.audio_path and os.path.exists(job.audio_path):
        try:
            os.remove(job.audio_path)
        except Exception:
            pass

    db.delete(job)
    db.commit()
    return None


@router.post("/{job_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_job(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    if job.status in ("ready", "failed", "cancelled"):
        raise InvalidStateException("Job đã kết thúc, không thể hủy.")

    job.status = "cancelled"
    db.commit()
    return {"job_id": str(job.id), "status": "cancelled"}


@router.get("/{job_id}/transcript", response_model=TranscriptResponse)
def get_transcript(
    job_id: uuid.UUID,
    pass_number: int = Query(2, alias="pass"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    segments = (
        db.query(Segment)
        .filter(Segment.job_id == job_id, Segment.pass_number == pass_number)
        .order_by(Segment.position)
        .all()
    )

    speakers = db.query(SpeakerAlias).filter(SpeakerAlias.job_id == job_id).all()
    highlights = db.query(Highlight).filter(Highlight.job_id == job_id).all()
    action_items = db.query(ActionItem).filter(ActionItem.job_id == job_id).all()

    # Build response with words
    segment_dtos = []
    for s in segments:
        words = db.query(Word).filter(Word.segment_id == s.id).order_by(Word.position).all()
        s_dto = SegmentItem(
            id=s.id,
            pass_number=s.pass_number,
            position=s.position,
            start_ms=s.start_ms,
            end_ms=s.end_ms,
            text_raw=s.text_raw,
            text_cleaned=s.text_cleaned,
            text_edited=s.text_edited,
            speaker_label=s.speaker_label,
            words=[WordItem.model_validate(w) for w in words],
        )
        segment_dtos.append(s_dto)

    return TranscriptResponse(
        segments=segment_dtos,
        speakers=[SpeakerAliasItem.model_validate(spk) for spk in speakers],
        highlights=[HighlightItem.model_validate(hl) for hl in highlights],
        action_items=[ActionItemDto.model_validate(ai) for ai in action_items],
    )


@router.patch("/{job_id}/segments/{position}")
def patch_segment(
    job_id: uuid.UUID,
    position: int,
    req: PatchSegmentRequest,
    pass_number: int = Query(2, alias="pass"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    segment = (
        db.query(Segment)
        .filter(Segment.job_id == job_id, Segment.pass_number == pass_number, Segment.position == position)
        .first()
    )
    if not segment:
        raise NotFoundException("Segment không tồn tại.")

    segment.text_edited = req.text_edited
    db.commit()
    return {"status": "ok", "position": position, "text_edited": segment.text_edited}


@router.patch("/{job_id}/speakers/{speaker_label}")
def patch_speaker(
    job_id: uuid.UUID,
    speaker_label: str,
    req: PatchSpeakerRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    alias = (
        db.query(SpeakerAlias)
        .filter(SpeakerAlias.job_id == job_id, SpeakerAlias.speaker_label == speaker_label)
        .first()
    )
    if not alias:
        alias = SpeakerAlias(
            job_id=job_id,
            speaker_label=speaker_label,
            display_name=req.display_name.strip(),
            source="manual",
        )
        db.add(alias)
    else:
        alias.display_name = req.display_name.strip()
        alias.source = "manual"

    db.commit()
    return {"speaker_label": speaker_label, "display_name": alias.display_name}


@router.post("/{job_id}/highlights", status_code=status.HTTP_201_CREATED)
def create_highlight(
    job_id: uuid.UUID,
    req: CreateHighlightRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    highlight = Highlight(
        id=uuid.uuid4(),
        job_id=job_id,
        segment_id=req.segment_id,
        quote=req.quote,
        start_ms=req.start_ms,
        end_ms=req.end_ms,
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(highlight)
    db.commit()
    return HighlightItem.model_validate(highlight)


@router.delete("/{job_id}/highlights/{highlight_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_highlight(
    job_id: uuid.UUID,
    highlight_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    hl = db.query(Highlight).filter(Highlight.id == highlight_id, Highlight.job_id == job_id).first()
    if hl:
        db.delete(hl)
        db.commit()
    return None


@router.post("/{job_id}/action-items", status_code=status.HTTP_201_CREATED)
def create_action_item(
    job_id: uuid.UUID,
    req: CreateActionItemRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    item = ActionItem(
        id=uuid.uuid4(),
        job_id=job_id,
        segment_id=req.segment_id,
        start_ms=req.start_ms,
        owner=req.owner or "",
        task=req.task,
        deadline=req.deadline or "",
        source="manual",
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(item)
    db.commit()
    return ActionItemDto.model_validate(item)


@router.patch("/{job_id}/action-items/{item_id}")
def update_action_item(
    job_id: uuid.UUID,
    item_id: uuid.UUID,
    req: PatchActionItemRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(ActionItem).filter(ActionItem.id == item_id, ActionItem.job_id == job_id).first()
    if not item:
        raise NotFoundException("Việc cần làm không tồn tại.")

    if req.task is not None:
        item.task = req.task
    if req.owner is not None:
        item.owner = req.owner
    if req.deadline is not None:
        item.deadline = req.deadline

    db.commit()
    return ActionItemDto.model_validate(item)


@router.delete("/{job_id}/action-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_action_item(
    job_id: uuid.UUID,
    item_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(ActionItem).filter(ActionItem.id == item_id, ActionItem.job_id == job_id).first()
    if item:
        db.delete(item)
        db.commit()
    return None


@router.post("/{job_id}/media-token", response_model=MediaTokenResponse)
def create_media_token(
    job_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    raw_token = generate_random_token()
    token_hashed = hash_token(raw_token)
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)

    rec = MediaToken(token_hash=token_hashed, job_id=job_id, expires_at=expires_at)
    db.add(rec)
    db.commit()

    return MediaTokenResponse(token=raw_token, expires_in=3600)


@router.get("/{job_id}/audio")
def stream_audio(
    job_id: uuid.UUID,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    token_hashed = hash_token(token)
    now = datetime.datetime.now(datetime.timezone.utc)
    token_rec = (
        db.query(MediaToken)
        .filter(MediaToken.token_hash == token_hashed, MediaToken.job_id == job_id, MediaToken.expires_at > now)
        .first()
    )
    if not token_rec:
        raise UnauthorizedException("Media token không hợp lệ hoặc đã hết hạn.")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.audio_path or not os.path.exists(job.audio_path):
        raise NotFoundException("File âm thanh không tồn tại.")

    return FileResponse(job.audio_path, media_type="audio/ogg")
