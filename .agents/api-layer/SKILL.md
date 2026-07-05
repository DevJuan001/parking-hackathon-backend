---
name: api-layer
description: Routes, middlewares, rate limiting, response shapes and CORS for parking-hackathon-backend. Load when adding/changing endpoints, middlewares, or response formats.
---

# API layer

## Boot

`app/main.py`:

- `lifespan` (async context manager) initializes Redis (`init_redis(app)`) and `FastAPILimiter.init(redis)`. Closes Redis in the `finally`.
- CORS: `allow_origins=["http://localhost:5173"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`. **Do not** change `allow_origins` without coordinating with the frontend.
- Health: `GET /` (`API funcionando`) and `GET /ping-db` (opens and closes a MySQL connection).
- Each feature is included with `app.include_router(<feature>_routes.router)`.

## Router

```python
from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.middlewares.onboarding_middleware import require_onboarded

router = APIRouter(prefix="/api/<domain>", tags=["<Domain>"])
```

- **Plural** prefix: `/api/users`, `/api/entries`, `/api/payments`, `/api/parking`, `/api/floors`, `/api/spots`, `/api/tariffs`, `/api/countries`, `/api/exits`, `/api/auth`.
- Kebab-case in paths: `/complete-on-boarding`, `/by-stats`, `/recent-entries`.
- `tags` in plural and capitalized: `["Users"]`, `["Entries"]`, `["Tariffs"]`.

## Rate limiting

`fastapi-limiter` with `Depends(RateLimiter(times=N, seconds=60))` applied **inside `dependencies=[...]`** in the route decorator.

Typical values already in the repo:

| Endpoint | Rate |
|---|---|
| `/api/auth/login` | 10/min |
| `/api/auth/register` | 3/min |
| `/api/auth/recover-password` | 3/min |
| `/api/auth/refresh` | 30/min |
| `/api/auth/complete-on-boarding` | 5/min |
| `/api/users/*` (general) | 30/min |
| `/api/users/update-password` | 10/min |
| `/api/floors/create|update|delete` | 10/min |
| `/api/spots/` (listing) | 300/min (high, consumed by dashboard) |
| rest | 30/min |

Rule of thumb: 30/min for admin endpoints, 10/min for sensitive actions, 100+ for dashboard reads.

## Middlewares (Depends)

Recommended order inside `dependencies=[...]`:

```python
dependencies=[
    Depends(RateLimiter(times=30, seconds=60)),  # first
    Depends(require_roles(["Admin"])),
    Depends(require_onboarded),                   # last
],
```

`verify_jwt` is not in `dependencies`; it is requested as a **parameter** of the function to get the `payload: dict`:

```python
def get_x(
    filters: XFiltersSchema = Depends(),
    payload: dict = Depends(verify_jwt),
):
```

## Response shapes

**Reads (lists or objects):**

```json
{ "data": [...]|{...} }
```

**Mutations (POST/PUT/DELETE):**

```json
{ "success": true, "message": "X creado correctamente" }
```

**Special endpoints:**

- `POST /api/auth/register` → `{"success": true, "message": "...", "onboarding_completed": false}`
- `PUT /api/auth/complete-on-boarding` → `{"success": true, "message": "...", "onboarding_completed": true}`
- `GET /api/users/me` → `{"data": {...}, "onboarding_completed": true}`

**HTTP codes** (repo rule):

- 200 GET / 200 PUT with body.
- 200 POST (not 201) in this repo.
- 400 invalid input / business rule.
- 401 invalid token or credentials (see `auth-and-security`).
- 403 unauthorized role / incomplete onboarding.
- 404 not found or empty listing with error.

**Error body:**

```json
{ "detail": "Message in Spanish" }
```

(Standard FastAPI `HTTPException` shape.)

## Filters as query params

```python
class XFiltersSchema(BaseModel):
    status: Optional[int] = None
    start_date: Optional[date] = None

@router.get("/", dependencies=[...])
def get_all(
    filters: XFiltersSchema = Depends(),
    payload: dict = Depends(verify_jwt),
):
    return XController.get_all(filters, payload)
```

FastAPI maps `?status=2&start_date=2024-01-01` to the schema. The service passes it to the repository, which does `model_dump(exclude_none=True)` and builds the dynamic query.

## Body params

```python
class CreateXSchema(BaseModel):
    name: str = safe_str(min_length=1, max_length=100)

@router.post("/create", dependencies=[...])
async def create_x(
    x_data: CreateXSchema,
    payload: dict = Depends(verify_jwt),
):
    return await XController.create_x(x_data, payload)
```

- If the endpoint is purely sync (no Celery/email/async IO), keep it sync.
- `async def` only if there is an internal `await`. (Several repo endpoints are `async` even when they don't `await` because they call an async service that may enqueue an email — copy that pattern only with a real reason.)

## Path params

```python
@router.get("/{x_id}")
def get_x(x_id: int, payload: dict = Depends(verify_jwt)):
    return XController.get_x(x_id, payload)
```

FastAPI validates the type. For IDs that come as `int` in the URL, declare the type in the signature.

## Swagger / OpenAPI

- `FastAPI(title="API con FastAPI y MySQL", description="Api para tracklinker", version="1.0.0", lifespan=lifespan)`. If you touch the version, also `pyproject.toml`.
- `/docs` (Swagger UI) and `/redoc` come by default.
- The router `tags` appear as a section in Swagger.

## CORS

If the frontend changes origin, **add it** to `allow_origins`. Do not use `["*"]` because it breaks `allow_credentials=True`.

## Rate limiter and Redis

`FastAPILimiter` requires Redis initialized in `lifespan`. If `lifespan` fails, the server **does not start** — the global `get_redis()` is `None` and rate limits break. That's why `init_redis` happens at startup.

## What is NOT done

- No extra auth on `/docs/*` endpoints: they are open by default.
- No `HTTPException(detail={"data": ...})` for successful responses — always `return {...}`.
- No custom ASGI middleware (logging, request id, etc.) unless asked.
- No `allow_origins=["*"]`.
