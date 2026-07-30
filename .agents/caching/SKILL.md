---
name: caching
description: Redis-backed caching helpers in parking-hackathon-backend (`app/core/cache.py`). Load when deciding whether to cache an endpoint or invalidating a cache. Note: the cache API is currently ORPHANED — no callers in the repo.
---

# Caching

## Status — ORPHANED CODE

`app/core/cache.py` is currently **orphaned**: a `grep -r "set_cache\|get_cache\|invalidate_cache" app/` shows only the definitions in `app/core/cache.py` itself — no endpoint, service, or feature imports the helpers. Before wiring it in, verify the helpers are still compatible with the current Redis init in `app/core/redis.py` (the helpers take a `redis` client as the first argument, so any caller must have an `AsyncRedis` instance in scope).

Treat this skill as a **reference for the intended API**, not as documentation of in-use behavior. If you add the first caller, update this skill with the file path and the use case.

## API (`app/core/cache.py`)

```python
async def set_cache(redis, key: str, data, ex: int = 20) -> None
async def get_cache(redis, key: str) -> Any | None
async def invalidate_cache(redis, pattern: str) -> None
```

- **Storage**: Redis (async, `AsyncRedis` from `redis.asyncio`).
- **Serialization**: internal `_serialize(obj)` handles `pydantic.BaseModel`, `list`, and `dict` recursively. Falls through to `json.dumps` for everything else.
- **TTL**: `ex` is in **seconds** (the Redis `EX` argument). Default is 20s — short by design, assume hot data.
- **Key**: caller-supplied string. There is no namespacing in the helper itself — namespace it at the call site (e.g. `cache:spots:{parking_id}:{page}`).

## When to use

Cache only after you can prove the endpoint is the bottleneck. Candidates in the current repo:

- Dashboard listings with high read traffic (`GET /api/spots/`, `GET /api/entries/`, `GET /api/exits/`) — see `api-layer` for the rate limits.
- Aggregate stats endpoints (`/api/entries/by-stats`, parking-level daily summary).
- Endpoints that join many tables and return slowly changing data.

When you cache, **commit a benchmark before and after** to prove the cache is earning its keep. The repo is not at a scale where speculative caching pays off.

## When NOT to use

- **Write endpoints.** They are the source of truth — invalidation always wins.
- **Per-user dashboards.** Cache key explosion (`cache:dashboard:{parking_id}:{user_id}:{role}`) and invalidation complexity. Compute on demand.
- **Real-time data.** `GET /api/entries/` filtered by today's date, `GET /api/exits/`, payment calculations — the staleness window is larger than the freshness requirement.
- **Auth-sensitive paths.** `verify_jwt` and `require_onboarded` must run every time; don't wrap them.
- **Anything behind a tight rate limit** (e.g. `/api/auth/login` 10/min). The Redis write cost is comparable to the work saved.

## Calling pattern (intended)

```python
from app.core.redis import get_redis
from app.core.cache import get_cache, set_cache, invalidate_cache

async def list_spots_cached(parking_id: int, page: int):
    redis = await get_redis()
    key = f"cache:spots:{parking_id}:{page}"

    cached = await get_cache(redis, key)
    if cached is not None:
        return cached

    data = await _fetch_spots(parking_id, page)
    await set_cache(redis, key, data, ex=30)
    return data
```

For invalidation, `invalidate_cache` uses Redis `KEYS <pattern>` + `DEL`. **`KEYS` is O(N)** — keep the pattern specific (e.g. `cache:spots:{parking_id}:*`) and call it only after a write that affects the cached scope. For high-throughput invalidation, switch to `SCAN`.

## Anti-patterns

- **Caching without an invalidation path.** Stale data is worse than no cache. If you cannot describe the invalidation trigger in one sentence, do not cache.
- **Caching per-user data with a global key.** The first user wins, everyone else reads their data.
- **Caching with no TTL on volatile data.** Without `ex`, the entry lives until you delete it (or Redis runs out of memory and evicts).
- **Caching pydantic models with custom types** (e.g. `datetime`, `Decimal`). `_serialize` falls through to `json.dumps` and will raise. Convert to `str` / `float` before storing.
- **Wrapping the Redis call in a `try/except` that swallows errors.** If Redis is down, fall back to the slow path loudly. A silent cache miss is fine; a silent cache failure looks like a working cache.
- **Adding a new cache helper to `app/core/cache.py` for one endpoint.** Inline the call at the use site; promote to a helper only when two endpoints share the pattern.

## Common errors

- `json.dumps(...)` raises on a `datetime` → convert to ISO string at the call site.
- `redis.keys(pattern)` returns empty after a write → the keys were written with a different pattern (e.g. typo in the namespace prefix).
- `RuntimeError: Redis no inicializado` from `get_redis()` → the `lifespan` did not run, or `init_redis` failed. Check `app/main.py`.

## Required environment variables

- `REDIS_URL` (see `config-and-settings`).
