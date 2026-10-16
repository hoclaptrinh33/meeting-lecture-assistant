"""Dependencies dùng chung cho các API endpoints."""
from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Dependency trích xuất và xác thực User hiện tại từ JWT Bearer token.
    TODO: Triển khai kiểm tra Bearer token và lấy User từ DB.
    """
    pass
