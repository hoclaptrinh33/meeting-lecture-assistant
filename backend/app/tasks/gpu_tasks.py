"""Tác vụ Celery bất đồng bộ cho hàng đợi GPU."""
from app.worker import celery_app


@celery_app.task(bind=True, name="app.tasks.transcribe_upload", max_retries=100)
def transcribe_upload(self, job_id_str: str):
    """Xử lý toàn bộ pipeline cho job tải file (PT1):
    1. Thử lấy GPU lock (nếu bận thì self.retry(countdown=5))
    2. Chuẩn hóa Opus và tạo memmap PCM float32
    3. Cắt chunk VAD và nhận dạng Whisper large-v3-turbo
    4. Giải phóng Whisper khỏi VRAM
    5. Chạy pyannote diarization (fallback CPU nếu OOM)
    6. Khớp speaker và so sánh hồ sơ giọng
    7. Hoàn tất job và giải phóng GPU lock.
    TODO: Triển khai pipeline.
    """
    pass


@celery_app.task(bind=True, name="app.tasks.run_live_session")
def run_live_session(self, session_id_str: str):
    """Xử lý phiên nghe trực tiếp PT2:
    TODO: Triển khai xử lý luồng âm thanh live và tổng hợp pass 2.
    """
    pass


@celery_app.task(bind=True, name="app.tasks.enroll_voice")
def enroll_voice(self, profile_id_str: str):
    """Trích xuất voice embedding và đăng ký hồ sơ giọng nói:
    TODO: Triển khai trích xuất embedding từ file mẫu.
    """
    pass
