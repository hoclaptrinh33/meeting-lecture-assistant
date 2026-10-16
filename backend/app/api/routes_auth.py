import datetime
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.security import (
    create_access_token,
    generate_random_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models import RefreshToken, User
from app.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _issue_tokens(user: User, db: Session) -> TokenResponse:
    access_token = create_access_token(user.id)
    raw_refresh = generate_random_token()
    token_hashed = hash_token(raw_refresh)

    refresh_rec = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=token_hashed,
        expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=settings.REFRESH_TOKEN_DAYS),
    )
    db.add(refresh_rec)
    db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_MINUTES * 60,
        refresh_token=raw_refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    email_clean = req.email.lower().strip()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise ValidationException("Email đã được sử dụng.", fields={"email": "Email đã tồn tại trong hệ thống."})

    user = User(
        id=uuid.uuid4(),
        email=email_clean,
        password_hash=hash_password(req.password),
        display_name=req.display_name.strip(),
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _issue_tokens(user, db)


@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    email_clean = req.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise UnauthorizedException("Email hoặc mật khẩu không chính xác.")

    return _issue_tokens(user, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    hashed = hash_token(req.refresh_token)
    token_rec = db.query(RefreshToken).filter(RefreshToken.token_hash == hashed).first()

    now = datetime.datetime.now(datetime.timezone.utc)
    if not token_rec or token_rec.revoked_at is not None or token_rec.expires_at < now:
        raise UnauthorizedException("Refresh token không hợp lệ hoặc đã hết hạn.")

    # Thu hồi token cũ
    token_rec.revoked_at = now
    db.commit()

    user = db.query(User).filter(User.id == token_rec.user_id).first()
    if not user:
        raise UnauthorizedException("Người dùng không tồn tại.")

    return _issue_tokens(user, db)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    hashed = hash_token(req.refresh_token)
    token_rec = db.query(RefreshToken).filter(RefreshToken.token_hash == hashed).first()
    if token_rec and token_rec.revoked_at is None:
        token_rec.revoked_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()
    return None


@router.get("/me", response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
