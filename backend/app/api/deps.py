import uuid
from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.models import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Dependency trích xuất và xác thực User hiện tại từ JWT Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("Thiếu hoặc sai định dạng header Authorization.")

    token = authorization.split(" ", 1)[1]
    user_id = decode_access_token(token)
    if not user_id:
        raise UnauthorizedException("Token không hợp lệ hoặc đã hết hạn.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UnauthorizedException("Người dùng không tồn tại.")

    return user
