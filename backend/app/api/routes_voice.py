import datetime
import os
from pathlib import Path
from typing import List
import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import NotFoundException, UnsupportedMediaException
from app.models import User, VoiceProfile
from app.schemas.voice import VoiceProfileCreateResponse, VoiceProfileResponse
from app.tasks.gpu_tasks import enroll_voice

router = APIRouter(prefix="/api/voice-profiles", tags=["voice-profiles"])


@router.get("", response_model=List[VoiceProfileResponse])
def list_voice_profiles(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profiles = (
        db.query(VoiceProfile)
        .filter(VoiceProfile.user_id == user.id)
        .order_by(VoiceProfile.created_at.desc())
        .all()
    )
    return [VoiceProfileResponse.model_validate(p) for p in profiles]


@router.post("", response_model=VoiceProfileCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_voice_profile(
    name: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile_id = uuid.uuid4()
    voice_dir = Path(settings.DATA_DIR) / "voice" / str(user.id)
    voice_dir.mkdir(parents=True, exist_ok=True)
    sample_path = voice_dir / f"{profile_id}.opus"

    content = await file.read()
    with open(sample_path, "wb") as f:
        f.write(content)

    profile = VoiceProfile(
        id=profile_id,
        user_id=user.id,
        display_name=name.strip()[:80],
        status="processing",
        sample_path=str(sample_path),
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(profile)
    db.commit()

    # Đẩy tác vụ trích xuất embedding vào Celery GPU
    enroll_voice.delay(str(profile_id))

    return VoiceProfileCreateResponse(
        id=profile.id,
        display_name=profile.display_name,
        status="processing",
    )


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_voice_profile(
    profile_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(VoiceProfile).filter(VoiceProfile.id == profile_id, VoiceProfile.user_id == user.id).first()
    if not profile:
        raise NotFoundException("Hồ sơ giọng không tồn tại.")

    if profile.sample_path and os.path.exists(profile.sample_path):
        try:
            os.remove(profile.sample_path)
        except Exception:
            pass

    db.delete(profile)
    db.commit()
    return None
