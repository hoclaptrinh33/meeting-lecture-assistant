"""Kết nối Redis và hỗ trợ Pub/Sub."""
from typing import Any, AsyncGenerator
import redis
import redis.asyncio as aioredis
from app.core.config import settings

# Khởi tạo client kết nối Redis
sync_redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
async_redis_pool = aioredis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)


def get_async_redis() -> aioredis.Redis:
    """Lấy async redis client."""
    return aioredis.Redis(connection_pool=async_redis_pool)


async def publish_event(channel: str, message: Any) -> int:
    """Publish sự kiện lên Redis Pub/Sub.
    TODO: Triển khai phát message qua Redis Pub/Sub.
    """
    pass


async def subscribe_events(channel: str) -> AsyncGenerator[str, None]:
    """Lắng nghe sự kiện từ kênh Redis Pub/Sub.
    TODO: Triển khai subscribe kênh và yield dữ liệu.
    """
    yield ""
