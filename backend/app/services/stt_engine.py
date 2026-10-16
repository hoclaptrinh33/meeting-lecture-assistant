import gc
from typing import Any, Dict, Generator, List, Optional
import numpy as np

from app.core.config import settings


class SttEngine:
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name or settings.WHISPER_MODEL
        self.device = device or settings.WHISPER_DEVICE
        self.compute_type = settings.WHISPER_COMPUTE_TYPE
        self.model = None

    def load_model(self) -> None:
        """Nạp model faster-whisper vào bộ nhớ."""
        if self.model is None:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
                download_root=settings.HF_HOME,
            )

    def unload_model(self) -> None:
        """Giải phóng hoàn toàn Whisper khỏi VRAM để nhường chỗ cho Pyannote."""
        if self.model is not None:
            del self.model
            self.model = None
            gc.collect()
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

    def transcribe_audio_chunk(
        self,
        audio_data: np.ndarray,
        time_offset_s: float = 0.0,
        vocabulary: Optional[str] = None,
        beam_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Nhận dạng một chunk audio và cộng offset thời gian vào từng từ."""
        if self.model is None:
            self.load_model()

        beam = beam_size or (
            settings.WHISPER_BEAM_SIZE if self.model_name == settings.WHISPER_MODEL else settings.WHISPER_DRAFT_BEAM_SIZE
        )

        segments, _ = self.model.transcribe(
            audio_data,
            language="vi",
            beam_size=beam,
            word_timestamps=True,
            initial_prompt=vocabulary,
        )

        results = []
        for segment in segments:
            seg_start_ms = int((segment.start + time_offset_s) * 1000)
            seg_end_ms = int((segment.end + time_offset_s) * 1000)
            words = []
            if segment.words:
                for w in segment.words:
                    words.append({
                        "text": w.word.strip(),
                        "start_ms": int((w.start + time_offset_s) * 1000),
                        "end_ms": int((w.end + time_offset_s) * 1000),
                    })
            results.append({
                "start_ms": seg_start_ms,
                "end_ms": seg_end_ms,
                "text_raw": segment.text.strip(),
                "words": words,
            })

        return results
