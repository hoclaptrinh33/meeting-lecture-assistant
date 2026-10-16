"""Khóa phân tán GPU trên Redis đảm bảo chỉ 1 tiến trình chiếm dụng VRAM tại một thời điểm."""
from typing import Optional
import redis
from app.core.config import settings

GPU_LOCK_KEY = "gpu:lock"
GPU_LOCK_TTL = 30
GPU_HEARTBEAT_INTERVAL = 10


class GpuLock:
    def __init__(self, owner_id: str, redis_client: Optional[redis.Redis] = None):
        self.owner_id = str(owner_id)
        self.redis = redis_client or redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

    def acquire(self) -> bool:
        """Thử lấy khóa GPU bằng SET NX EX 30 và khởi động heartbeat.
        TODO: Triển khai lấy khóa phân tán và heartbeat gia hạn.
        """
        pass

    def release(self) -> bool:
        """Giải phóng khóa nếu giá trị vẫn là owner_id của mình.
        TODO: Triển khai kiểm tra và giải phóng khóa an toàn.
        """
        pass

    def __enter__(self):
        """Context manager vào khóa."""
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager thoát khóa."""
        pass
