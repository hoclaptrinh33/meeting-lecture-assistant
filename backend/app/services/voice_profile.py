from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from app.core.config import settings


class VoiceProfileService:
    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Tính độ tương đồng Cosine giữa 2 vector embedding."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    @classmethod
    def match_speaker_clusters(
        cls,
        speaker_embeddings: Dict[str, np.ndarray],
        user_profiles: List[Dict[str, Any]],
    ) -> Dict[str, str]:
        """Khớp các cụm người nói từ diarization với danh sách hồ sơ giọng của người dùng."""
        matches: Dict[str, str] = {}
        if not user_profiles or not speaker_embeddings:
            return matches

        for speaker_label, cluster_emb in speaker_embeddings.items():
            scores: List[Tuple[float, str]] = []
            for profile in user_profiles:
                p_emb = np.frombuffer(profile["embedding"], dtype=np.float32)
                sim = cls.cosine_similarity(cluster_emb, p_emb)
                scores.append((sim, profile["display_name"]))

            scores.sort(key=lambda x: x[0], reverse=True)
            if not scores:
                continue

            best_score, best_name = scores[0]
            if best_score >= settings.VOICE_MATCH_THRESHOLD:
                if len(scores) > 1:
                    second_score, _ = scores[1]
                    if (best_score - second_score) >= settings.VOICE_MATCH_MARGIN:
                        matches[speaker_label] = best_name
                else:
                    matches[speaker_label] = best_name

        return matches
