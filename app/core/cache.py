import json
from pydantic import BaseModel


def _serialize(obj):
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}
    return obj


async def set_cache(redis, key: str, data, ex: int = 20):
    await redis.set(key, json.dumps(_serialize(data)), ex=ex)


async def get_cache(redis, key: str):
    cached = await redis.get(key)
    return json.loads(cached) if cached else None


async def invalidate_cache(redis, pattern: str):
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)
