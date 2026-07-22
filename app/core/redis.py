from fastapi import FastAPI
import redis.asyncio as redis
from app.core.config import settings

redis_client: redis.Redis = None


async def get_redis() -> redis.Redis:
    return redis_client


async def init_redis(app: FastAPI):
    global redis_client
    redis_client = await redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=2,
        retry_on_timeout=True,
    )
    return redis_client


async def close_redis():
    global redis_client
    
    if redis_client:
        await redis_client.close()