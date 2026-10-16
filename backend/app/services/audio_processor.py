import json
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np

from app.core.config import settings
from app.core.exceptions import DurationExceededException, UnsupportedMediaException


class AudioProcessor:
    @staticmethod
    def probe_audio(input_path: str) -> Dict[str, float]:
        """Kiểm tra file âm thanh qua ffprobe: lấy thời lượng và xác thực stream."""
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=duration,sample_rate,channels:format=duration",
            "-of", "json",
            input_path,
        ]
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            info = json.loads(result.stdout)
        except Exception as e:
            raise UnsupportedMediaException("Không thể đọc định dạng âm thanh từ file.") from e

        streams = info.get("streams", [])
        if not streams:
            raise UnsupportedMediaException("File không chứa luồng âm thanh hợp lệ.")

        format_info = info.get("format", {})
        duration = None
        if "duration" in format_info and format_info["duration"] is not None:
            try:
                duration = float(format_info["duration"])
            except ValueError:
                pass

        if duration is None and "duration" in streams[0] and streams[0]["duration"] is not None:
            try:
                duration = float(streams[0]["duration"])
            except ValueError:
                pass

        if duration is None:
            raise DurationExceededException("Không thể xác định thời lượng file.")

        if duration > settings.MAX_DURATION_SECONDS:
            raise DurationExceededException(f"Thời lượng file ({duration:.1f}s) vượt quá giới hạn 3 giờ.")

        # Ước lượng kích thước PCM float32 16kHz mono (16000 samples * 4 bytes/sec = 64KB/sec)
        estimated_pcm_bytes = duration * 16000 * 4
        if estimated_pcm_bytes > 800 * 1024 * 1024:
            raise DurationExceededException("Kích thước PCM ước lượng vượt quá 800 MB.")

        return {
            "duration": duration,
            "duration_ms": int(duration * 1000),
            "sample_rate": float(streams[0].get("sample_rate", 16000)),
            "channels": int(streams[0].get("channels", 1)),
        }

    @staticmethod
    def normalize_to_canonical_opus(input_path: str, job_id: str) -> str:
        """Chuẩn hóa audio sang Opus 16 kHz mono 32 kb/s lưu trữ dài hạn."""
        audio_dir = Path(settings.DATA_DIR) / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        output_opus = audio_dir / f"{job_id}.opus"

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-vn",
            "-ac", "1",
            "-ar", "16000",
            "-c:a", "libopus",
            "-b:a", "32k",
            "-f", "ogg",
            str(output_opus),
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg chuyển đổi Opus thất bại: {e.stderr.decode('utf-8', errors='ignore')}")

        return str(output_opus)

    @staticmethod
    def create_pcm_f32_memmap(opus_path: str, job_id: str) -> Tuple[str, np.ndarray]:
        """Tạo file PCM float32le 16 kHz mono tạm thời để memmap vào model."""
        tmp_dir = Path(settings.DATA_DIR) / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        f32_path = tmp_dir / f"{job_id}.f32"

        cmd = [
            "ffmpeg", "-y",
            "-i", opus_path,
            "-f", "f32le",
            "-acodec", "pcm_f32le",
            "-ac", "1",
            "-ar", "16000",
            str(f32_path),
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg tạo PCM f32le thất bại: {e.stderr.decode('utf-8', errors='ignore')}")

        # Đọc memmap float32 [-1, 1]
        data = np.memmap(str(f32_path), dtype=np.float32, mode="r")
        return str(f32_path), data

    @staticmethod
    def cleanup_temp_f32(job_id: str) -> None:
        """Xóa file PCM tạm thời khi job hoàn tất hoặc thất bại."""
        f32_path = Path(settings.DATA_DIR) / "tmp" / f"{job_id}.f32"
        if f32_path.exists():
            try:
                os.remove(f32_path)
            except Exception:
                pass
