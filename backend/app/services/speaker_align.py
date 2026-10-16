from collections import Counter
from typing import Any, Dict, List, Optional


class SpeakerAligner:
    @staticmethod
    def align_words_and_segments(
        segments: List[Dict[str, Any]],
        speaker_turns: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Gán nhãn người nói cho từng từ và xác định người nói chính cho từng câu."""
        if not speaker_turns:
            return segments

        for seg in segments:
            seg_words = seg.get("words", [])
            seg_speaker_votes: List[str] = []

            for word in seg_words:
                w_start = word["start_ms"]
                w_end = word["end_ms"]
                w_len = max(1, w_end - w_start)

                best_speaker = None
                max_overlap = 0

                for turn in speaker_turns:
                    t_start = turn["start_ms"]
                    t_end = turn["end_ms"]
                    # Tính khoảng giao nhau
                    overlap = max(0, min(w_end, t_end) - max(w_start, t_start))
                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_speaker = turn["speaker_label"]

                if best_speaker and (max_overlap / w_len) > 0.3:
                    word["speaker_label"] = best_speaker
                    seg_speaker_votes.append(best_speaker)
                else:
                    word["speaker_label"] = None

            # Nhãn người nói đại diện của câu là nhãn chiếm đa số số từ
            if seg_speaker_votes:
                counts = Counter(seg_speaker_votes)
                seg["speaker_label"] = counts.most_common(1)[0][0]
            else:
                # Nếu từ chưa khớp, tìm turn giao nhiều nhất với cả segment
                seg_start = seg["start_ms"]
                seg_end = seg["end_ms"]
                best_speaker = None
                max_overlap = 0
                for turn in speaker_turns:
                    t_start = turn["start_ms"]
                    t_end = turn["end_ms"]
                    overlap = max(0, min(seg_end, t_end) - max(seg_start, t_start))
                    if overlap > max_overlap:
                        max_overlap = overlap
                        best_speaker = turn["speaker_label"]
                seg["speaker_label"] = best_speaker

        return segments
