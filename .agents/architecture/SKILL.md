---
name: architecture
description: Project structure, layers and request flow for the parking-hackathon-backend. Read this before changing where a file lives or adding a new module.
---

# Architecture

## Overview

A FastAPI 3-layer backend with **feature modules** instead of "controllers/services" at the top level. The shape is:

```
route  →  controller  →  service  →  repository  →  MySQL
                          ↓
                       cache (Redis)
                          ↓
                       tasks (Celery + email)
```

The frontend lives at `http://localhost:5173` (CORS allow-listed in `app/main.py:43`).

## Folder layout

```
app/
├── main.py               # FastAPI instance, lifespan, CORS, /, /ping-db, include_router
├── core/                 # cross-cutting infra
├── middlewares/          # FastAPI dependencies
├── features/<domain>/    # one folder per business domain
├── tasks/                # Celery tasks
├── templates/            # HTML email templates
└── utils/                # pure helpers (logger, plate_formatter, safe_types, …)
```

### `app/core/`

- `config.py` — `Settings(BaseSettings)` loads `.env`. Access: `from app.core.config import settings`.
- `database.py` — `get_connection()` returns a raw `mysql.connector` connection (no ORM). It is called once at import to validate at startup.
- `redis.py` — `init_redis(app)`, `close_redis()`, `get_redis()`. Initialized in `lifespan` (`main.py:24`).
- `cache.py` — `set_cache / get_cache / invalidate_cache` (serializes pydantic models to JSON).
- `celery_app.py` — `celery = Celery("worker", broker=REDIS_URL, …)`.
- `mail.py` — `ConnectionConfig` SMTP (Gmail STARTTLS, port 587) and `fm = FastMail(config)`.
- `security.py` — `create_access_token`, `create_refresh_token`, `set_auth_cookies`, `verify_password`, `generate_temporal_password`.
- `token_blacklist.py` — Redis blacklist for access/refresh tokens (TTL = what's left on the token).
- `exception.py` — `class ServiceError(Exception)` with `self.message`.

### `app/middlewares/`

These are FastAPI **Depends**, not ASGI middlewares.

- `verify_jwt` (`jwt_middleware.py`) — reads `access_token` from the cookie, validates, **queries the DB** for `parking_id` and `onboarding_completed`, returns `{"user_id","role","parking_id","onboarding_completed"}`.
- `require_roles(["Admin", "Cliente"])` — factory that returns a Depends validating the role.
- `require_onboarded` — Depends that requires `payload["onboarding_completed"] == True`.

### `app/features/<domain>/` — the internal shape

Each feature **always** has the same structure (use `app/features/parking/` or `app/features/entries/` as reference):

```
features/<domain>/
├── controllers/<domain>_controller.py   # HTTPException translation + response shape
├── services/<domain>_service.py         # Business logic + transactions
├── repositories/<domain>_repository.py  # Raw SQL with mysql.connector
├── routes/<domain>_routes.py            # APIRouter, RateLimiter, middlewares
└── models/
    ├── <domain>_schemas.py              # Pydantic: inputs (create, update, filters)
    └── <domain>_responses.py            # Pydantic: outputs
```

`app/features/parking/` is special: it groups **3 repositories** (parkings, plates, vehicle_types) under the same public domain.

## Request flow

1. **Route** (`features/<x>/routes/<x>_routes.py`)
   - Declares `APIRouter(prefix="/api/<x>", tags=[...])`.
   - Applies `RateLimiter(times, seconds)`, `require_roles([...])`, `require_onboarded` as `dependencies=[Depends(...)]`.
   - Extracts `payload: dict = Depends(verify_jwt)` and pydantic schemas.
   - Calls the controller.

2. **Controller** (`features/<x>/controllers/<x>_controller.py`)
   - Translates the `(error, data[, success, message])` tuple from the service into `HTTPException` or JSON.
   - Returns the agreed shape: `{"data": ...}` for reads, `{"success": ..., "message": ...}` for mutations.

3. **Service** (`features/<x>/services/<x>_service.py`)
   - Calls `connection = get_connection()`.
   - `try / except ServiceError / except Exception / finally: connection.close()`.
   - Calls the repository, validates, decides on `commit()` or `rollback()`.
   - Returns a tuple, never raises HTTP.

4. **Repository** (`features/<x>/repositories/<x>_repository.py`)
   - Receives an already-open `connection`.
   - `cursor = connection.cursor()`, executes SQL with `%s`, maps to pydantic models.
   - Closes the cursor in `finally`.
   - Returns a tuple `(error, data[, ...])` and never touches `commit/rollback`.

## Multi-tenant

`payload["parking_id"]` (injected by `verify_jwt` from the DB) is the **only** valid `parking_id` in any query. It is not accepted in the body nor as a path param. Any repository touching parking data receives `parking_id` as an argument.

## Cross-feature imports

- Services may import other services or repositories from another feature (e.g. `EntriesService` uses `PlatesRepository` and `SpotsRepository`).
- Repositories **do not** import services or controllers.
- Models (pydantic) are free but watch out for cycles.

## Where NOT to put logic

- SQL in controllers or services: **always** in a repository.
- Pydantic in repositories: **yes**, they map `cursor.fetchall()` to a `Response`.
- `commit/rollback` in repositories: **no**, lives in the service.
- `HTTPException` in services: **no**, they return a tuple or `raise ServiceError(...)`.
