---
name: feature-scaffold
description: How to add a new feature module to parking-hackathon-backend following the routes → controllers → services → repositories convention. Load when creating a new endpoint or domain.
---

# Feature scaffold

Every new feature follows **exactly** the same shape. Before starting, look at `app/features/parking/` (full case with sub-repositories) or `app/features/tariffs/` (simple case). Follow the `requirement-design-implementation` skill flow before touching files.

## Required structure

```
app/features/<domain>/
├── __init__.py
├── controllers/
│   └── <domain>_controller.py
├── services/
│   └── <domain>_service.py
├── repositories/
│   └── <domain>_repository.py
├── routes/
│   └── <domain>_routes.py
└── models/
    ├── __init__.py
    ├── <domain>_schemas.py
    └── <domain>_responses.py
```

If the feature has several repos (like `parking/` with `parkings_repository`, `plates_repository`, `vehicle_types_repository`), put them all under `repositories/`.

## File templates

### `models/<domain>_schemas.py`

Pydantic schemas for inputs. **Every user string** goes through `safe_str` / `safe_optional_str`.

```python
from typing import Optional
from pydantic import BaseModel
from app.utils.safe_types import safe_str, safe_optional_str

class CreateXSchema(BaseModel):
    name: str = safe_str(min_length=1, max_length=100)

class UpdateXSchema(BaseModel):
    name: Optional[str] = safe_optional_str(min_length=1, max_length=100)

class XFiltersSchema(BaseModel):
    status: Optional[int] = None
```

### `models/<domain>_responses.py`

```python
from pydantic import BaseModel

class XResponse(BaseModel):
    id: int
    name: str
    created_at: str
```

### `repositories/<domain>_repository.py`

```python
from app.utils.logger import get_logger
from app.utils.date_formatter import date_formatter
from app.features.<domain>.models.<domain>_responses import XResponse

logger = get_logger("<domain>.repository")


class XRepository:

    @staticmethod
    def find_all_x(parking_id: int, connection):
        cursor = connection.cursor()
        query = """
        SELECT id, name, created_at
        FROM X
        WHERE parking_id = %s
        ORDER BY created_at DESC
        """
        try:
            cursor.execute(query, (parking_id,))
            results = cursor.fetchall()
            data = [XResponse(id=r[0], name=r[1], created_at=date_formatter(r[2])) for r in results]
            return None, data
        except Exception as e:
            logger.error("Error en find_all_x: %s", e, exc_info=True)
            return "Error al intentar obtener …", None
        finally:
            cursor.close()

    @staticmethod
    def create_x(name: str, parking_id: int, connection):
        cursor = connection.cursor()
        query = "INSERT INTO X (name, parking_id) VALUES (%s, %s)"
        try:
            cursor.execute(query, (name, parking_id))
            return None, cursor.lastrowid, "X creado correctamente"
        except Exception as e:
            logger.error("Error en create_x: %s", e, exc_info=True)
            return "Error al intentar crear X", None, None
        finally:
            cursor.close()
```

Rules:

- Receives an already-open `connection`.
- `cursor` in `try / except / finally` with `cursor.close()` in `finally`.
- `cursor.execute(query, (...,))` with `%s`. **Never** f-strings.
- Returns tuple `(error, data[, ...])`.
- **Does not** `commit` or `rollback`.

### `services/<domain>_service.py`

```python
from app.utils.logger import get_logger
from app.core.exception import ServiceError
from app.core.database import get_connection
from app.features.<domain>.repositories.<domain>_repository import XRepository

logger = get_logger("<domain>.service")


class XService:

    @staticmethod
    def get_all_x(parking_id: int):
        connection = get_connection()
        try:
            error, data = XRepository.find_all_x(parking_id, connection)
            if error:
                raise ServiceError(error)
            return None, data
        except ServiceError as e:
            return e.message, None
        except Exception as e:
            logger.error("Error en get_all_x: %s", e, exc_info=True)
            return "Error al intentar obtener …", None
        finally:
            connection.close()

    @staticmethod
    def create_x(parking_id: int, name: str):
        connection = get_connection()
        try:
            error, x_id, msg = XRepository.create_x(name, parking_id, connection)
            if error or not x_id:
                raise ServiceError(error or msg)
            connection.commit()
            return None, True, "X creado correctamente"
        except ServiceError as e:
            connection.rollback()
            return e.message, False, None
        except Exception as e:
            connection.rollback()
            logger.error("Error en create_x: %s", e, exc_info=True)
            return "Error al intentar crear X", False, None
        finally:
            connection.close()
```

Rules:

- `connection = get_connection()` **once** at the start of each method.
- `commit()` only when everything succeeded.
- `rollback()` in **every** `except`.
- `connection.close()` in `finally`.
- User-facing error messages in Spanish and friendly.
- Raise `ServiceError("…")` for business errors; any other error falls into `except Exception`.

### `controllers/<domain>_controller.py`

```python
from fastapi import HTTPException
from app.features.<domain>.services.<domain>_service import XService
from app.features.<domain>.models.<domain>_schemas import CreateXSchema


class XController:

    @staticmethod
    def get_all_x(payload: dict):
        error, data = XService.get_all_x(int(payload["parking_id"]))
        if error:
            raise HTTPException(status_code=404, detail=error)
        return {"data": data}

    @staticmethod
    async def create_x(x_data: CreateXSchema, payload: dict):
        error, success, message = await XService.create_x(
            int(payload["parking_id"]), x_data.name
        )
        if error:
            raise HTTPException(status_code=400, detail=error)
        return {"success": success, "message": message}
```

Rules:

- `payload["parking_id"]` always as `int(...)` before passing to the service.
- 404 for "not found" / empty listings with error.
- 400 for input / business rules.
- Shape: `{"data": …}` or `{"success": …, "message": …}`.

### `routes/<domain>_routes.py`

```python
from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from app.middlewares.jwt_middleware import verify_jwt
from app.middlewares.roles_middleware import require_roles
from app.middlewares.onboarding_middleware import require_onboarded
from app.features.<domain>.controllers.<domain>_controller import XController
from app.features.<domain>.models.<domain>_schemas import CreateXSchema, XFiltersSchema

router = APIRouter(prefix="/api/<domain>", tags=["<Domain>"])


@router.get(
    "/",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
        Depends(require_onboarded),
    ],
)
def get_all_x(
    filters: XFiltersSchema = Depends(),
    payload: dict = Depends(verify_jwt),
):
    return XController.get_all_x(payload)


@router.post(
    "/create",
    dependencies=[
        Depends(RateLimiter(times=30, seconds=60)),
        Depends(require_roles(["Admin"])),
    ],
)
async def create_x(
    x_data: CreateXSchema,
    payload: dict = Depends(verify_jwt),
):
    return await XController.create_x(x_data, payload)
```

Rules:

- **Plural** prefix, kebab-case if it has multiple words.
- `dependencies=[Depends(...)]` for `RateLimiter`, `require_roles`, `require_onboarded`. Order: rate limit first, then role, then onboarding.
- Async endpoints only if you call something async (Celery, email, etc.). For purely sync flows, **keep it sync** (the current pattern in the repo).
- The payload is always extracted as `payload: dict = Depends(verify_jwt)`.

### `app/main.py`

Add the include:

```python
from app.features.<domain>.routes import <domain>_routes
...
app.include_router(<domain>_routes.router)
```

## Advanced patterns

- **Sub-repos in the same feature** (`parking/`): a single `service` and `controller` orchestrate several `repositories` (plates, vehicle_types, parkings). Repos do not import each other.
- **Filters as query params**: declare the schema in `models/_schemas.py` with `Optional` fields and pass it to the route as `filters: XFiltersSchema = Depends()`. Inside the repo, `filters_data.model_dump(exclude_none=True)` and concatenate `AND` to the query.
- **Partial update**: `data = user_data.model_dump(exclude_none=True)`, build dynamically `SET col1 = %s, col2 = %s` only with the present fields, append the IDs at the end.
- **Multi-table in one transaction**: pass the same `connection` to several repos. They all commit or rollback together.
- **Onboarding** (see `auth-and-security`): some routes do not require `require_onboarded` (e.g. `complete-on-boarding`, login, register, refresh, recover-password).

## Anti-patterns (do not do)

- Do not create a generic `BaseRepository`. It does not exist in the repo and adding it now is scope creep.
- Do not create an ORM. The repo uses raw SQL on purpose.
- Do not create automatic tests unless asked. If you do, they will be `pytest` and won't need elaborate fixtures.
- Do not return plain `dict` instead of `(error, data)` tuples.
- Do not `commit()` in the repository. Always in the service.
