"""Khớp nhãn người nói với mốc thời gian của từng từ và từng câu."""
from typing import Any, Dict, List


class SpeakerAligner:
    @staticmethod
    def align_words_and_segments(
        segments: List[Dict[str, Any]],
        speaker_turns: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Gán nhãn người nói cho từng từ và xác định người nói chính cho từng câu.
        TODO: Triển khai thuật toán tính độ giao thoa thời gian (overlap) giữa word và speaker turn.
        """
        pass
