---
name: pagination
description: Pagination pattern (per_page + page with LIMIT/OFFSET) used in parking-hackathon-backend listings. Load when adding a paginated endpoint or modifying an existing one.
---

# Pagination

## Pattern

The repo uses a simple `page` + `per_page` schema, applied as `LIMIT %s OFFSET %s` in the SQL. There is **no cursor pagination** anywhere in the codebase — every list endpoint uses this pattern.

Schema (in `app/features/<x>/models/<x>_schemas.py`):

```python
from typing import Optional
from pydantic import BaseModel, Field

class XFiltersSchema(BaseModel):
    status: Optional[int] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(15, ge=1, le=100)
```

Defaults and ranges:

- `page`: `Field(1, ge=1)`. Always 1-indexed. The first page is `?page=1`.
- `per_page`: depends on the feature.
  - `entries`, `exits`, `users`: default `15`, max `100`.
  - `spots`: default `56` (the dashboard renders a grid), max `100`.
  - `reservations`: default `50`, max `100`.

Pydantic enforces the bounds. A request with `?per_page=999` returns `400` from FastAPI before the route runs.

## Where it's used

Grep `per_page` in the repo (currently five features paginate):

| Feature | `per_page` default | File |
|---|---|---|
| `entries` | 15 | `app/features/entries/models/entries_schemas.py:13` |
| `exits` | 15 | `app/features/exits/models/exits_schemas.py:13` |
| `users` | 15 | `app/features/users/models/users_schemas.py:19` |
| `spots` | 56 | `app/features/spots/models/spots_schemas.py:11` |
| `reservations` | 50 | `app/features/reservations/models/reservations_schemas.py:14` |
| `payments` | — (no pagination; `PaymentsFiltersSchema` has no `page` / `per_page`) | `app/features/payments/models/payments_schemas.py:9-13` |

**`payments` does not paginate** — the filter schema (`app/features/payments/models/payments_schemas.py:9-13`) has no `page` or `per_page`; the listing endpoint returns the full filtered result set. If the payments table grows, add the same pattern as `entries` — do not assume pagination already exists.

## Repo example (`entries_repository.find_all_entries`)

```python
@staticmethod
def find_all_entries(parking_id: int, filters_data: EntriesFiltersSchema, connection):
    cursor = connection.cursor()

    data = filters_data.model_dump(exclude_none=True)

    query = """
    SELECT
        e.id, p.plate, vt.id, s.spot_id, s.spot, e.created_at
    FROM ENTRIES AS e
    INNER JOIN PLATES AS p            ON p.id  = e.plate_id
    INNER JOIN VEHICLE_TYPES AS vt    ON vt.id = p.vehicle_type_id
    INNER JOIN SPOTS AS s             ON s.spot_id = e.spot_id
    """

    filters = ["e.parking_id = %s"]
    values = [parking_id]

    if "plate_id" in data:
        filters.append("p.id = %s")
        values.append(data["plate_id"])
    # ... more optional filters ...

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY e.id DESC LIMIT %s OFFSET %s"

    per_page = filters_data.per_page
    offset = (filters_data.page - 1) * per_page
    values += [per_page, offset]

    try:
        cursor.execute(query, values)
        results = cursor.fetchall()
        # ... build responses ...
        return None, entries
    except Exception as e:
        logger.error("Error en find_all_entries: %s", e, exc_info=True)
        return "Error al intentar obtener los ingresos", None
    finally:
        cursor.close()
```

Key points:

- `ORDER BY` is always **before** `LIMIT/OFFSET`, otherwise pagination is non-deterministic.
- `LIMIT %s OFFSET %s` are positional `%s` placeholders, never f-strings. The values go at the **end** of the `values` list.
- `offset = (filters_data.page - 1) * filters_data.per_page`. Always 1-indexed on the input, 0-indexed in SQL.
- The response shape is the same `{"data": [...]}` (see `api-layer`). The frontend computes the next/prev URL from `page` and `per_page`.

## Response shape (current)

The repo currently returns only the slice. The frontend tracks `page` / `per_page` and counts locally. The response is:

```json
{
  "data": [
    { "id": 1, "plate": "ABC123", "created_at": "2024-01-15T10:30:00" }
  ]
}
```

There is **no `total` / `total_pages` / `next_page` envelope** today. If the frontend needs a total, add a `count_*` repository method and a separate `/by-stats` endpoint rather than enriching the listing response (consistent with the existing `by-stats` pattern).

## Anti-patterns

- **No max cap on `per_page`**. Without `le=100` (or another ceiling), a client can request 10,000 rows and exhaust MySQL + memory. Always set a max.
- **Page-only with no per_page**. `?page=5` alone is ambiguous — the server picks an arbitrary size. Always send both.
- **Using `OFFSET` for large pages**. `OFFSET 100000` still scans the first 100,000 rows. If a feature ever needs deep pagination, switch to keyset pagination (`WHERE id < :last_id ORDER BY id DESC LIMIT :n`). Not needed today.
- **Echoing `page` in the response without `per_page`**. The frontend can't compute "next page" without both. Keep them in the query string.
- **Sorting by a non-unique column without a tiebreaker**. `ORDER BY name` produces a non-deterministic order across pages. Always sort by an indexed unique column (`id`, `created_at DESC, id DESC`).
- **Caching paginated responses with a key that omits `page`**. Every page reads the same cached entry.

## When to add pagination

Add it when the table can grow unbounded. The current `reservations` table is small but the dashboard lists `spots` (`per_page=56`) — that's the right default. If a feature gets a "list all" endpoint, add pagination **before** shipping the endpoint, not after.

## Common errors

- `Out of sort memory` from MySQL → `ORDER BY` is on an unindexed column. Add an index matching the sort.
- Duplicate rows across pages → the `ORDER BY` column is not unique. Add a tiebreaker (`id`).
- `Incorrect arguments to mysqld_stmt_execute` → you passed `per_page` / `offset` as a string instead of `int`. The `Field(..., ge=1)` constraint already enforces int.
- Frontend sees page 1 empty but page 2 has data → you wrote `LIMIT %s OFFSET %s` with the values in the wrong order, or `OFFSET` is `page * per_page` instead of `(page - 1) * per_page`.

## Required environment variables

None — pagination is in the SQL and the Pydantic schema.
