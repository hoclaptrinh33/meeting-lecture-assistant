import gc
from typing import Any, Dict, List, Optional
from app.core.config import settings


class DiarizationService:
    def __init__(self, hf_token: Optional[str] = None):
        self.hf_token = hf_token or settings.HF_TOKEN

    def diarize_audio(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Phân đoạn người nói bằng pyannote.audio dòng 3.1. Rơi về CPU nếu CUDA OOM."""
        if not self.hf_token:
            return {
                "device": "skipped",
                "turns": [],
                "warning": "HF_TOKEN chưa được cấu hình, bỏ qua phân đoạn người nói.",
            }

        import torch
        from pyannote.audio import Pipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token,
                cache_dir=settings.HF_HOME,
            )
            if device == "cuda":
                pipeline.to(torch.device("cuda"))
        except Exception as e:
            return {
                "device": "error",
                "turns": [],
                "warning": f"Không thể tải pipeline pyannote: {str(e)}",
            }

        params = {}
        if num_speakers is not None and 1 <= num_speakers <= 20:
            params["num_speakers"] = num_speakers

        try:
            diarization = pipeline(audio_path, **params)
            used_device = device
        except torch.cuda.OutOfMemoryError:
            # Fallback sang CPU nếu OOM trên CUDA
            gc.collect()
            torch.cuda.empty_cache()
            pipeline.to(torch.device("cpu"))
            diarization = pipeline(audio_path, **params)
            used_device = "cpu"
        except Exception as e:
            return {
                "device": "error",
                "turns": [],
                "warning": f"Quá trình phân đoạn người nói thất bại: {str(e)}",
            }

        turns = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            turns.append({
                "start_ms": int(turn.start * 1000),
                "end_ms": int(turn.end * 1000),
                "speaker_label": speaker,
            })

        # Giải phóng bộ nhớ
        del pipeline
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return {
            "device": used_device,
            "turns": turns,
            "warning": None,
        }
