import json
from typing import Any, AsyncGenerator, Optional
import redis
import redis.asyncio as aioredis
from app.core.config import settings

# Đồng bộ (Sync) cho Celery worker & scripts
sync_redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Bất đồng bộ (Async) cho FastAPI SSE và WebSocket
async_redis_pool = aioredis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)


def get_async_redis() -> aioredis.Redis:
    """Lấy async redis client."""
    return aioredis.Redis(connection_pool=async_redis_pool)


async def publish_event(channel: str, message: Any) -> int:
    """Publish sự kiện lên Redis Pub/Sub."""
    r = get_async_redis()
    serialized = json.dumps(message) if not isinstance(message, str) else message
    return await r.publish(channel, serialized)


async def subscribe_events(channel: str) -> AsyncGenerator[str, None]:
    """Lắng nghe sự kiện từ kênh Redis Pub/Sub."""
    r = get_async_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                yield message["data"]
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
