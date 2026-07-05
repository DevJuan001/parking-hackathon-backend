import hashlib
from datetime import datetime, timezone

import jwt

from app.core.redis import get_redis


BLACKLIST_PREFIX = "blacklist:access_token:"


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_token_remaining_ttl(token: str) -> int:
    try:
        payload = jwt.decode(token, options={"verify_signature": False})

        exp = payload.get("exp")

        if exp is None:
            return 0

        remaining = int(exp - datetime.now(timezone.utc).timestamp())

        return max(0, remaining)
    except Exception:
        
        return 0


async def add_to_blacklist(token: str, ttl_seconds: int) -> bool:
    if ttl_seconds <= 0:
        return False

    try:
        redis = await get_redis()

        key = BLACKLIST_PREFIX + _hash_token(token)

        await redis.set(key, "1", ex=ttl_seconds)

        return True

    except Exception:
        return False


async def is_blacklisted(token: str) -> bool:
    redis = await get_redis()

    key = BLACKLIST_PREFIX + _hash_token(token)

    return bool(await redis.exists(key))
