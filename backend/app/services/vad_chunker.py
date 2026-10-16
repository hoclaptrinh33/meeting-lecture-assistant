from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

# Silero VAD parameters
VAD_THRESHOLD = 0.5
MIN_SPEECH_DURATION_MS = 250
MIN_SILENCE_DURATION_MS = 400
SPEECH_PAD_MS = 200

# Project chunking constants (seconds)
MIN_CHUNK_S = 20.0
MAX_CHUNK_S = 30.0
OVERLAP_S = 1.0
MAX_GAP_S = 2.0
MIN_TAIL_S = 0.3
SAMPLE_RATE = 16000


@dataclass
class SpeechInterval:
    start_s: float
    end_s: float


@dataclass
class AudioChunk:
    chunk_index: int
    start_s: float
    end_s: float
    start_sample: int
    end_sample: int


class VadChunker:
    @staticmethod
    def chunk_audio(
        speech_intervals: List[SpeechInterval],
        total_duration_s: float,
    ) -> List[AudioChunk]:
        """Gom các đoạn tiếng nói (speech intervals) từ VAD thành các chunk 20-30 giây."""
        chunks: List[AudioChunk] = []
        if not speech_intervals:
            # Nếu không tìm thấy tiếng nói, chia đều 30s
            curr = 0.0
            idx = 0
            while curr < total_duration_s:
                end = min(curr + MAX_CHUNK_S, total_duration_s)
                if end - curr < MIN_TAIL_S:
                    break
                chunks.append(AudioChunk(
                    chunk_index=idx,
                    start_s=curr,
                    end_s=end,
                    start_sample=int(curr * SAMPLE_RATE),
                    end_sample=int(end * SAMPLE_RATE),
                ))
                idx += 1
                curr = end
            return chunks

        idx = 0
        current_chunk_start = speech_intervals[0].start_s
        current_chunk_end = speech_intervals[0].end_s

        for i in range(1, len(speech_intervals)):
            interval = speech_intervals[i]
            proposed_end = interval.end_s
            proposed_duration = proposed_end - current_chunk_start

            # Nếu thêm đoạn này mà vượt MAX_CHUNK_S, ta chốt chunk hiện tại
            if proposed_duration > MAX_CHUNK_S:
                if current_chunk_end - current_chunk_start >= MIN_TAIL_S:
                    chunks.append(AudioChunk(
                        chunk_index=idx,
                        start_s=current_chunk_start,
                        end_s=current_chunk_end,
                        start_sample=int(current_chunk_start * SAMPLE_RATE),
                        end_sample=int(current_chunk_end * SAMPLE_RATE),
                    ))
                    idx += 1
                # Bắt đầu chunk mới từ interval hiện tại
                current_chunk_start = interval.start_s
                current_chunk_end = interval.end_s
            else:
                # Nếu khoảng cách giữa 2 đoạn lớn hơn MAX_GAP_S và độ dài đã đạt MIN_CHUNK_S
                gap = interval.start_s - current_chunk_end
                if gap > MAX_GAP_S and (current_chunk_end - current_chunk_start) >= MIN_CHUNK_S:
                    chunks.append(AudioChunk(
                        chunk_index=idx,
                        start_s=current_chunk_start,
                        end_s=current_chunk_end,
                        start_sample=int(current_chunk_start * SAMPLE_RATE),
                        end_sample=int(current_chunk_end * SAMPLE_RATE),
                    ))
                    idx += 1
                    current_chunk_start = interval.start_s
                    current_chunk_end = interval.end_s
                else:
                    current_chunk_end = proposed_end

        # Thêm chunk cuối cùng nếu còn lại
        if current_chunk_end - current_chunk_start >= MIN_TAIL_S:
            chunks.append(AudioChunk(
                chunk_index=idx,
                start_s=current_chunk_start,
                end_s=min(current_chunk_end, total_duration_s),
                start_sample=int(current_chunk_start * SAMPLE_RATE),
                end_sample=int(min(current_chunk_end, total_duration_s) * SAMPLE_RATE),
            ))

        return chunks
