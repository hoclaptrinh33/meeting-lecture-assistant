import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

# Khởi tạo PasswordHasher với thuật toán argon2id
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng argon2id."""
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Xác thực mật khẩu với chuỗi hash argon2id."""
    try:
        return ph.verify(hashed_password, password)
    except (VerifyMismatchError, Exception):
        return False


def hash_token(token: str) -> str:
    """Tính mã SHA-256 của token để lưu trữ an toàn trong DB."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_random_token() -> str:
    """Tạo chuỗi token ngẫu nhiên an toàn."""
    return f"{uuid.uuid4().hex}{uuid.uuid4().hex}"


def create_access_token(user_id: uuid.UUID, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT access token có thời hạn."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)
    
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> Optional[uuid.UUID]:
    """Giải mã access token và trích xuất user_id."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            return None
        return uuid.UUID(sub)
    except (jwt.PyJWTError, ValueError):
        return None
