"""Động cơ nhận dạng tiếng nói sử dụng faster-whisper (Large-v3-Turbo / Small)."""
from typing import Any, Dict, List, Optional
import numpy as np


class SttEngine:
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name
        self.device = device
        self.model = None

    def load_model(self) -> None:
        """Nạp model faster-whisper vào VRAM.
        TODO: Khởi tạo WhisperModel với tham số int8 và tải checkpoint.
        """
        pass

    def unload_model(self) -> None:
        """Giải phóng hoàn toàn Whisper khỏi VRAM để nhường chỗ cho Pyannote.
        TODO: Thu hồi bộ nhớ và gọi torch.cuda.empty_cache().
        """
        pass

    def transcribe_audio_chunk(
        self,
        audio_data: np.ndarray,
        time_offset_s: float = 0.0,
        vocabulary: Optional[str] = None,
        beam_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Nhận dạng một chunk audio và cộng offset thời gian vào từng từ.
        TODO: Gọi model.transcribe với word_timestamps=True và initial_prompt.
        """
        pass
