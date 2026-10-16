"""Xác thực, bảo mật, băm mật khẩu và JWT token."""
from datetime import timedelta
from typing import Optional
import uuid


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng argon2id.
    TODO: Triển khai logic băm mật khẩu.
    """
    pass


def verify_password(password: str, hashed_password: str) -> bool:
    """Xác thực mật khẩu với chuỗi hash argon2id.
    TODO: Triển khai kiểm tra mật khẩu.
    """
    pass


def hash_token(token: str) -> str:
    """Tính mã SHA-256 của token để lưu trữ an toàn trong DB.
    TODO: Triển khai băm token SHA-256.
    """
    pass


def generate_random_token() -> str:
    """Tạo chuỗi token ngẫu nhiên an toàn.
    TODO: Triển khai tạo token ngẫu nhiên.
    """
    pass


def create_access_token(user_id: uuid.UUID, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT access token có thời hạn.
    TODO: Triển khai tạo JWT token.
    """
    pass


def decode_access_token(token: str) -> Optional[uuid.UUID]:
    """Giải mã access token và trích xuất user_id.
    TODO: Triển khai giải mã JWT token.
    """
    pass
