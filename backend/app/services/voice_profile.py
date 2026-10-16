"""Nhận dạng người nói theo hồ sơ giọng nói (Voice Profiles) qua so khớp Cosine Similarity."""
from typing import Any, Dict, List
import numpy as np


class VoiceProfileService:
    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Tính độ tương đồng Cosine giữa 2 vector embedding.
        TODO: Triển khai dot(a, b) / (norm(a) * norm(b)).
        """
        pass

    @classmethod
    def match_speaker_clusters(
        cls,
        speaker_embeddings: Dict[str, np.ndarray],
        user_profiles: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Khớp các cụm người nói từ diarization với danh sách hồ sơ giọng của người dùng.
        TODO: Triển khai so sánh điểm Cosine với ngưỡng VOICE_MATCH_THRESHOLD và VOICE_MATCH_MARGIN.
        """
        pass
