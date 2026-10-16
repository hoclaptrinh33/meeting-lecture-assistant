import urllib.parse
import uuid
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models import ActionItem, Highlight, Job, LlmRun, Segment, SpeakerAlias, User
from app.schemas.export import ExportRequest
from app.services.exporter import ExporterService

router = APIRouter(prefix="/api/jobs", tags=["export"])

MIME_TYPES = {
    "md": "text/markdown; charset=utf-8",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
    "srt": "application/x-subrip; charset=utf-8",
    "vtt": "text/vtt; charset=utf-8",
}


@router.post("/{job_id}/exports")
def export_job_document(
    job_id: uuid.UUID,
    req: ExportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user.id).first()
    if not job:
        raise NotFoundException("Job không tồn tại.")

    # Lấy các segment pass 2
    segments_db = (
        db.query(Segment)
        .filter(Segment.job_id == job_id, Segment.pass_number == 2)
        .order_by(Segment.position)
        .all()
    )

    # Lấy speaker alias map
    aliases = db.query(SpeakerAlias).filter(SpeakerAlias.job_id == job_id).all()
    alias_map = {a.speaker_label: a.display_name for a in aliases}

    segment_dicts = []
    for s in segments_db:
        segment_dicts.append({
            "position": s.position,
            "start_ms": s.start_ms,
            "end_ms": s.end_ms,
            "text_raw": s.text_raw,
            "text_cleaned": s.text_cleaned,
            "text_edited": s.text_edited,
            "speaker_label": s.speaker_label,
            "speaker_display": alias_map.get(s.speaker_label, s.speaker_label),
        })

    # Lấy tóm tắt mới nhất nếu có
    latest_summary_run = (
        db.query(LlmRun)
        .filter(LlmRun.job_id == job_id, LlmRun.task == "summarize", LlmRun.status == "done")
        .order_by(LlmRun.finished_at.desc())
        .first()
    )
    summary_data = latest_summary_run.result if latest_summary_run else None

    # Lấy highlights & action items
    highlights = db.query(Highlight).filter(Highlight.job_id == job_id).all()
    hl_dicts = [{"quote": h.quote, "start_ms": h.start_ms, "end_ms": h.end_ms} for h in highlights]

    actions = db.query(ActionItem).filter(ActionItem.job_id == job_id).all()
    act_dicts = [{"task": a.task, "owner": a.owner, "deadline": a.deadline, "start_ms": a.start_ms} for a in actions]

    fmt = req.format
    if fmt == "srt":
        file_bytes = ExporterService.export_srt(segment_dicts, req.text, req.include_speakers)
    elif fmt == "vtt":
        file_bytes = ExporterService.export_vtt(segment_dicts, req.text, req.include_speakers)
    elif fmt == "md":
        file_bytes = ExporterService.export_markdown(
            job.title, segment_dicts, summary_data, hl_dicts, act_dicts, req.text, req.include_speakers
        )
    elif fmt == "docx":
        file_bytes = ExporterService.export_docx(
            job.title, segment_dicts, summary_data, act_dicts, req.text, req.include_speakers
        )
    elif fmt == "pdf":
        file_bytes = ExporterService.export_pdf(
            job.title, segment_dicts, summary_data, req.text, req.include_speakers
        )
    else:
        raise NotFoundException(f"Định dạng {fmt} không được hỗ trợ.")

    filename = f"{job.title}.{fmt}"
    encoded_filename = urllib.parse.quote(filename)

    return Response(
        content=file_bytes,
        media_type=MIME_TYPES[fmt],
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
        },
    )
