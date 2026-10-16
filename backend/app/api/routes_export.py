"""API xuất tài liệu transcript và biên bản ra file tải về."""
import uuid
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.export import ExportRequest

router = APIRouter(prefix="/api/jobs", tags=["export"])


@router.post("/{job_id}/exports")
def export_job_document(
    job_id: uuid.UUID,
    req: ExportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xuất transcript và biên bản ra định dạng file tương ứng (md, docx, pdf, srt, vtt).
    TODO: Lấy segments và tóm tắt, gọi ExporterService và trả Response kèm Content-Disposition.
    """
    pass
