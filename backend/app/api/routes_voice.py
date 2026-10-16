"""API hồ sơ đặc trưng giọng nói (Voice Profiles)."""
from typing import List
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.voice import VoiceProfileCreateResponse, VoiceProfileResponse

router = APIRouter(prefix="/api/voice-profiles", tags=["voice-profiles"])


@router.get("", response_model=List[VoiceProfileResponse])
def list_voice_profiles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lấy danh sách hồ sơ giọng của tài khoản hiện tại.
    TODO: Lấy danh sách VoiceProfile của user.
    """
    pass


@router.post("", response_model=VoiceProfileCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_voice_profile(
    name: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Tải file mẫu giọng và đăng ký hồ sơ mới.
    TODO: Lưu file mẫu vào /data/voice, tạo VoiceProfile và đẩy task enroll_voice.
    """
    pass


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_voice_profile(
    profile_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Xóa hồ sơ giọng và file âm thanh mẫu liên quan.
    TODO: Xóa file mẫu và bản ghi VoiceProfile.
    """
    pass
