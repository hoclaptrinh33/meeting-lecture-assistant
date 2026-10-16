"""Tác vụ Celery bất đồng bộ cho hàng đợi IO (gọi LLM ngoài)."""
from app.worker import celery_app


@celery_app.task(bind=True, name="app.tasks.run_llm")
def run_llm(self, run_id_str: str):
    """Xử lý các tác vụ LLM (clean transcript, summarize) trên hàng IO:
    1. Đọc dữ liệu câu transcript từ DB
    2. Gửi request sang LLM_BASE_URL
    3. Cập nhật kết quả hoặc lỗi vào DB.
    TODO: Triển khai pipeline gọi LLM.
    """
    pass
