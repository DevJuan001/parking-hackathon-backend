---
name: code-conventions
description: Naming, returns, error handling, logging and Pydantic patterns used across the parking-hackathon-backend. Apply on every new or changed file.
---

# Code conventions

## Languages

- **Code** (names, technical docstrings, internal logs): **English**.
- **User-facing messages** (HTTPException, return `{"message": ...}`): **Spanish**, friendly.
- **Commits**: Spanish or English, consistent with the repo (see `git log`).

## Naming

- Feature folders: `app/features/<domain>/` (singular, lowercase).
- Classes: `PascalCase`. One class per file when it represents a layer (`XxxController`, `XxxService`, `XxxRepository`).
- Methods: `snake_case`.
- `static` methods on services, controllers and repositories — no `self`, they are groups of functions.
- SQL tables: `UPPER_SNAKE` (`PLATES`, `VEHICLE_TYPES`).
- Endpoints: kebab-case in paths (`/complete-on-boarding`, `/by-stats`).
- Schemas: `<Verb><Entity>Schema` (`CreateEntrySchema`, `EntriesFiltersSchema`).
- Responses: `<Entity>Response` (`EntryResponse`, `UserStatsResponse`).

## Logger

Always at the top of each repository/service/controller file:

```python
from app.utils.logger import get_logger
logger = get_logger("<module>.<layer>")
```

Examples from the repo: `"auth.service"`, `"plates.repository"`, `"users.service"`.

Usage:

```python
logger.error("Error en create_plate: %s", e, exc_info=True)
```

**Never** loose `print(...)`. **Never** `logger.info` with sensitive data (passwords, tokens).

## Pydantic — user strings

Every text input coming from the client **must** go through `safe_*`:

```python
from app.utils.safe_types import safe_str, safe_optional_str, safe_list_str, safe_optional_list_str

class CreateEntrySchema(BaseModel):
    plate: str = safe_str(min_length=6, max_length=6)

class UpdateUserSchema(BaseModel):
    name: Optional[str] = safe_optional_str(max_length=100)
```

`safe_*` validates + sanitizes: blocks HTML tags, `javascript:`, event handlers, SQL-injection-like patterns (`--`, `union select`, `or 1=1`) and control characters. Don't reinvent this.

`safe_str(...)` and friends return a `FieldInfo`, not a string: use them as **default values** in pydantic (`= safe_str(...)`), not as functions.

## Pydantic — responses

- Responses are **mapped in the repository** from `cursor.fetchall()` / `fetchone()`.
- Dates: use `date_formatter(item[N])` (format `Mes DD AAAA` in Spanish) unless the response asks for ISO `datetime` (`EntryResponse.created_at: datetime`).
- `BaseSchema` (in `app/utils/base_schema.py`) converts `date` to `str` in the `mode="before"` validator — use it when you need to accept `date` in a response.
- `Optional[...]` for fields that may be missing (`plate` optional in `SpotResponse`).

## Pydantic — fixed-set strings (Literal + types/ module)

For fields whose value comes from a small, finite set of strings (e.g. `provider = "Local" | "Google" | "GitHub"`), use a `Literal` type alias in a dedicated **`types/`** module per feature. **Never** put the set as an inline `Literal[...]` annotation in the schema or the service — the same set will be needed in three places (input schema, response model, repository) and duplicating it causes silent drift.

**The pattern**, in 3 files:

```python
# app/features/<feature>/types/<feature>_types.py
from typing import Literal, get_args

MyFieldType = Literal["A", "B", "C"]
VALID_MY_FIELDS: frozenset[str] = frozenset(get_args(MyFieldType))
```

```python
# app/features/<feature>/models/<feature>_responses.py
from app.features.<feature>.types.<feature>_types import MyFieldType

class MyResponse(BaseModel):
    my_field: MyFieldType
```

```python
# app/features/<feature>/repositories/<feature>_repository.py
from app.features.<feature>.types.<feature>_types import MyFieldType, VALID_MY_FIELDS

def create_thing(..., my_field: MyFieldType, ...):
    # Defensa en profundidad: validar ANTES de tocar la DB.
    # Un typo como "gogle" o "Github" (sin H) se rechaza acá.
    if my_field not in VALID_MY_FIELDS:
        logger.error(
            "MyField inválido '%s'. Valores válidos: %s. "
            "Esto es un bug en el código que llama a create_thing.",
            my_field, sorted(VALID_MY_FIELDS),
        )
        return (
            "No se pudo crear el elemento. Intentalo nuevamente más tarde.",
            False, None,
        )
    # ... INSERT INTO ...
```

**Rules**:

- The `Literal` is the **single source of truth** for the set. Adding a new value (e.g. `"D"`) is a one-line change in `types/<feature>_types.py`. Pydantic, the response model, and the runtime check all pick it up automatically.
- `Literal` is a **type hint only** in Python — it is not enforced at runtime. `frozenset(get_args(Literal[...]))` extracts the set so the repository can validate before the SQL hits the DB.
- The user-facing message on a validation failure is **generic** ("No se pudo crear el elemento..."). The technical detail (which value, which set) goes to `logger.error`, never to the API response. This prevents leaking the set of valid values to a potential attacker.
- The validation lives in the **repository**, not the service or the schema. This makes it impossible to bypass: every caller of `create_*` is protected, including future ones (admin endpoints, Celery tasks, scripts, tests).
- **Do not** add `provider`-style fields to `CreateXSchema` (the input schema). The set is a service-layer concern, not an API consumer concern. See the worked example in `auth-and-security/SKILL.md` for why.

**Worked example in the repo**: `app/features/users/types/users_types.py` defines `ProviderType = Literal["Local", "Google", "GitHub"]` and `VALID_PROVIDERS`. Both `users_responses.py` and `users_repository.py` import from it. The runtime check is in `users_repository.py:create_user`.

## Plates

```python
from app.utils.plate_formatter import plate_formatter
plate_text = plate_formatter(plate_data.plate)  # uppercase + no "-"
```

Before hitting the DB, also validate: `len(plate_text) == 6`, `plate_text[:3].isalpha()`, derive `vehicle_type_id` by the last character (1=moto if digit, 2=car if letter).

## Money

```python
from app.utils.round_to_50 import round_up_to_next_50
total = round_up_to_next_50(value_raw)
```

`0` and negatives return `50` (minimum billable). Always pass the result through this function before persisting or returning.

## Errors — canonical flow

### Service

```python
try:
    ...
    if some_bad_condition:
        raise ServiceError("Clear and friendly message in Spanish")
    ...
    connection.commit()
    return None, data          # reads
    return None, True, "ok"   # mutations
except ServiceError as e:
    connection.rollback()
    return e.message, None[, False, None]
except Exception as e:
    connection.rollback()
    logger.error("Error en <method>: %s", e, exc_info=True)
    return "Error al intentar <action>", None[, False, None]
finally:
    connection.close()
```

`ServiceError` lives in `app/core/exception.py`.

### Controller

```python
error, data = Service.some_method(...)
if error:
    raise HTTPException(status_code=404, detail=error)  # read
return {"data": data}

# mutation
error, success, message = Service.other_method(...)
if error:
    raise HTTPException(status_code=400, detail=error)
return {"success": success, "message": message}
```

- 400 → input/validation, business rule.
- 401 → unauthenticated or invalid token (emitted by `verify_jwt`).
- 403 → unauthorized role / onboarding not completed.
- 404 → not found.

### Response shapes

- Reads: `{"data": <list | object>}`.
- Mutations: `{"success": bool, "message": str}`.
- Special cases: `complete_onboarding` adds `"onboarding_completed": True`, `get_me` adds `"onboarding_completed": bool`.

## Logging in SQL

In repos, `logger.error("Error en <method>: %s", e, exc_info=True)` in the `except`, and always close the cursor in `finally`.

## Transactions — recap

- `get_connection()` in the **service**.
- `commit()` after all operations succeeded.
- `rollback()` in `except ServiceError` and `except Exception`.
- `close()` in `finally`.
- The cursor is opened and closed by the **repository** that uses it.
- If an operation touches several tables (e.g. `create_entry`: INSERT entry + UPDATE spot status), they go in the **same** `connection` and commit together.

## Conventional commits (summary, see dedicated skill)

`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`. Lowercase, concise message.

## Comments

- **Only** when the code does not explain itself. The repo does not use many comments.
- Don't comment the obvious. Do comment a SQL trick, a "why", a non-obvious decision.
- Never delete a comment without understanding why it was there.
