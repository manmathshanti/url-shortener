from typing import Optional

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

redis_client: Optional[aioredis.Redis] = None


async def get_redis_client() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


async def get_cached_url(short_code: str) -> Optional[str]:
    try:
        client = await get_redis_client()
        return await client.get(f"url:{short_code}")
    except Exception:
        return None


async def set_cached_url(short_code: str, original_url: str, ttl: Optional[int] = None) -> None:
    try:
        client = await get_redis_client()
        await client.setex(f"url:{short_code}", ttl or settings.redis_ttl, original_url)
    except Exception:
        pass


async def delete_cached_url(short_code: str) -> None:
    try:
        client = await get_redis_client()
        await client.delete(f"url:{short_code}")
    except Exception:
        pass


async def close_redis_connection() -> None:
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
