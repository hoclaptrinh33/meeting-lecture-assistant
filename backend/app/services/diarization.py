"""Dịch vụ phân đoạn người nói sử dụng pyannote.audio 3.1."""
from typing import Any, Dict, Optional


class DiarizationService:
    def __init__(self, hf_token: Optional[str] = None):
        self.hf_token = hf_token

    def diarize_audio(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Phân đoạn người nói bằng pyannote.audio dòng 3.1. Rơi về CPU nếu CUDA OOM.
        TODO: Triển khai nạp Pipeline pyannote/speaker-diarization-3.1 và trích xuất các lượt nói.
        """
        pass
