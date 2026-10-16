import threading
import time
from typing import Optional
import redis

from app.core.config import settings

GPU_LOCK_KEY = "gpu:lock"
GPU_LOCK_TTL = 30
GPU_HEARTBEAT_INTERVAL = 10

LUA_RELEASE_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""

LUA_EXTEND_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("expire", KEYS[1], ARGV[2])
else
    return 0
end
"""


class GpuLock:
    def __init__(self, owner_id: str, redis_client: Optional[redis.Redis] = None):
        self.owner_id = str(owner_id)
        if redis_client is None:
            self.redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        else:
            self.redis = redis_client
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_heartbeat = threading.Event()

    def acquire(self) -> bool:
        """Thử lấy khóa GPU bằng SET NX EX 30."""
        acquired = bool(self.redis.set(GPU_LOCK_KEY, self.owner_id, nx=True, ex=GPU_LOCK_TTL))
        if acquired:
            self._start_heartbeat()
        return acquired

    def _start_heartbeat(self) -> None:
        self._stop_heartbeat.clear()

        def heartbeat_loop():
            while not self._stop_heartbeat.wait(GPU_HEARTBEAT_INTERVAL):
                try:
                    result = self.redis.eval(LUA_EXTEND_SCRIPT, 1, GPU_LOCK_KEY, self.owner_id, GPU_LOCK_TTL)
                    if not result:
                        break
                except Exception:
                    pass

        self._heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def release(self) -> bool:
        """Giải phóng khóa nếu giá trị vẫn là owner_id của mình."""
        self._stop_heartbeat.set()
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=1.0)

        try:
            result = self.redis.eval(LUA_RELEASE_SCRIPT, 1, GPU_LOCK_KEY, self.owner_id)
            return bool(result)
        except Exception:
            return False

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"Could not acquire GPU lock for {self.owner_id}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
