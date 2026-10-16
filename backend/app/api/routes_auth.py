"""API xác thực người dùng (Đăng ký, Đăng nhập, Refresh token, Logout, Me)."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Đăng ký tài khoản mới.
    TODO: Triển khai kiểm tra email, băm mật khẩu, lưu User và trả token.
    """
    pass


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Đăng nhập lấy access token và refresh token.
    TODO: Triển khai kiểm tra thông tin đăng nhập và cấp token.
    """
    pass


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Cấp lại cặp token mới khi access token hết hạn.
    TODO: Triển khai thu hồi refresh token cũ và cấp token mới.
    """
    pass


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Đăng xuất và thu hồi refresh token.
    TODO: Triển khai đánh dấu revoked refresh token.
    """
    pass


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Lấy thông tin tài khoản đang đăng nhập.
    TODO: Trả về thông tin người dùng hiện tại.
    """
    pass
