"""Phát hiện tiếng nói (VAD) và chia cắt audio thành các chunk 20-30 giây."""
from dataclasses import dataclass
from typing import List

# Hằng số cấu hình VAD và chia chunk theo đặc tả
VAD_THRESHOLD = 0.5
MIN_SPEECH_DURATION_MS = 250
MIN_SILENCE_DURATION_MS = 400
SPEECH_PAD_MS = 200

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
        """Gom các đoạn tiếng nói (speech intervals) từ VAD thành các chunk 20-30 giây.
        TODO: Triển khai thuật toán cắt audio tại điểm lặng theo các hằng số dự án.
        """
        pass
