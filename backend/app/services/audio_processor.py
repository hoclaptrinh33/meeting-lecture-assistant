"""Xử lý âm thanh: kiểm tra ffprobe, chuẩn hóa Opus và tạo mảng PCM float32 memmap."""
from typing import Dict, Tuple
import numpy as np


class AudioProcessor:
    @staticmethod
    def probe_audio(input_path: str) -> Dict[str, float]:
        """Kiểm tra file âm thanh qua ffprobe: lấy thời lượng và xác thực stream.
        TODO: Triển khai gọi ffprobe, kiểm tra thời lượng và kích thước PCM ước lượng.
        """
        pass

    @staticmethod
    def normalize_to_canonical_opus(input_path: str, job_id: str) -> str:
        """Chuẩn hóa audio sang Opus 16 kHz mono 32 kb/s lưu trữ dài hạn.
        TODO: Triển khai chuyển đổi ffmpeg sang /data/audio/{job_id}.opus.
        """
        pass

    @staticmethod
    def create_pcm_f32_memmap(opus_path: str, job_id: str) -> Tuple[str, np.ndarray]:
        """Tạo file PCM float32le 16 kHz mono tạm thời để memmap vào model.
        TODO: Triển khai ffmpeg xuất ra /data/tmp/{job_id}.f32 và đọc memmap float32.
        """
        pass

    @staticmethod
    def cleanup_temp_f32(job_id: str) -> None:
        """Xóa file PCM tạm thời khi job hoàn tất hoặc thất bại.
        TODO: Triển khai xóa file /data/tmp/{job_id}.f32.
        """
        pass
