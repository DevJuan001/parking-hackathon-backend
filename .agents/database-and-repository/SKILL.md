---
name: database-and-repository
description: How database access works in parking-hackathon-backend: connection lifecycle, transactions, SQL style, and repository rules. Load before writing any SQL or touching transactions.
---

# Database & repository

## Driver and connection

- Driver: `mysql-connector-python` (sync). No ORM. No implicit `commit/rollback`.
- Helper: `get_connection()` in `app/core/database.py` → returns a `mysql.connector` connection with `charset="utf8mb4"` and `collation="utf8mb4_unicode_ci"`.
- `get_connection()` is called once on **import** to validate at startup (the current repo does this; keep it that way unless asked to change).

## Who handles the connection

| Layer | Connection | Cursor | `commit/rollback` | `close()` |
|---|---|---|---|---|
| `service` | **opens** with `get_connection()` | passes it to the repo | **yes**, decides | in `finally` |
| `repository` | receives it open | **opens/closes** | **no** | only `cursor.close()` |
| `controller` | does not touch | does not touch | does not touch | does not touch |
| `route` | does not touch | does not touch | does not touch | does not touch |

**`verify_jwt` is the only exception**: it opens and closes its own connection because it runs before the service.

## Repository template

```python
from app.utils.logger import get_logger
from app.utils.date_formatter import date_formatter
from app.features.<x>.models.<x>_responses import XResponse

logger = get_logger("<x>.repository")


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
            data = [
                XResponse(id=r[0], name=r[1], created_at=date_formatter(r[2]))
                for r in results
            ]
            return None, data
        except Exception as e:
            logger.error("Error en find_all_x: %s", e, exc_info=True)
            return "Error al intentar obtener …", None
        finally:
            cursor.close()
```

Rules (non-negotiable):

- `cursor = connection.cursor()` always inside the function.
- `cursor.close()` in `finally`.
- `try / except Exception / finally` — the `except` logs and returns an error tuple.
- Consistent return tuple: `(error, data)` for reads; `(error, success, message[, id])` for mutations.

## SQL — style

- Always `cursor.execute(query, values)` with `%s`. **Never** f-strings or `+`.
- Tenant filter: `WHERE parking_id = %s` or `INNER JOIN FLOORS f ON f.id = s.floor_id WHERE f.parking_id = %s` when the table does not have a direct `parking_id` (case of `SPOTS`).
- For queries with dynamic filters, build the list `filters = ["parking_id = %s"]` and `values = [parking_id]`, and concatenate with `AND`. Example: `entries_repository.find_all_entries`.
- Table aliases: `AS e`, `AS p`, `AS s` (entries, plates, spots). Stay consistent.
- UPPERCASE for reserved words and table/column names: `SELECT id, name FROM PLATES`.
- `value` strings in INSERT/UPDATE: `%s` with the tuple in order.
- `INSERT` returns `cursor.lastrowid` (int) on mutations.

## Transactions — recap

```python
connection = get_connection()
try:
    # validations / raises ServiceError
    # repository calls with `connection=connection`
    connection.commit()
    return None, True, "ok"
except ServiceError as e:
    connection.rollback()
    return e.message, False, None
except Exception as e:
    connection.rollback()
    logger.error(...)
    return "Error al intentar ...", False, None
finally:
    connection.close()
```

If an operation touches several tables (e.g. `create_entry`: INSERT entry + UPDATE spot), **same connection**, **single commit**. If the second repo fails, the first rolls back together.

## Dynamic filters

Pattern used in `entries`, `exits`, `payments`, `users`, `spots`:

```python
data = filters.model_dump(exclude_none=True)
filters_sql = ["e.parking_id = %s"]
values = [parking_id]

if "start_date" in data:
    filters_sql.append("DATE(e.created_at) >= %s")
    values.append(data["start_date"])
# ...

query += " WHERE " + " AND ".join(filters_sql)
cursor.execute(query, values)
```

## Order and cascading delete (logic)

There is no FK with `ON DELETE CASCADE` defined by SQLAlchemy (there is no SQLAlchemy). Delete is done by hand in the service:

- `delete_floor` → `count_occupied_spots_by_floor` (blocks if there are occupied) → `delete_spots_by_floor` → `delete_floor`. All in the same transaction.
- `delete_spot` → `find_spot_by_id` (blocks if `spot_status == 3`).
- `delete_tariff` → `count_active_vehicles_by_type` (blocks if there are actives).

When you add a new delete, decide whether the rule goes in the service (recommended) and keep it transactional.

## Counts / stats with `SUM(CASE …)`

Repo pattern for stats with `total/today/this_week/this_month`:

```sql
SELECT
    COUNT(*) AS total,
    SUM(CASE WHEN DATE(e.created_at) = CURDATE() THEN 1 ELSE 0 END) AS today,
    SUM(CASE WHEN e.created_at >= (NOW() - INTERVAL 7 DAY) THEN 1 ELSE 0 END) AS this_week,
    SUM(
        CASE WHEN YEAR(e.created_at) = YEAR(CURDATE())
                  AND MONTH(e.created_at) = MONTH(CURDATE())
             THEN 1 ELSE 0 END
    ) AS this_month
FROM ENTRIES AS e
WHERE e.parking_id = %s
```

And map to `EntryStatsResponse(total=…, today=…, this_week=…, this_month=…)`. For monetary sums use `COALESCE(SUM(value), 0)` and `float(result[N] or 0)`.

## `lastrowid`

In `INSERT`s, return `cursor.lastrowid` so the service can use it (e.g. `create_parking` needs it to create the default floor; `create_floor` doesn't, but `create_parking` does).

## `buffered=True`

`find_user_by_email` uses `cursor(buffered=True)` because it calls `fetchone()`. If you see `Unread result found` elsewhere, apply the same pattern.

## Driver errors

`mysql.connector.Error` is logged as `Exception` in the `except`. Nothing special: rollback, generic message to the user, log with `exc_info=True`.

## What is never done in the repo

- No explicit nested transactions.
- No `connection.commit()` from the repository.
- No `f"SELECT … WHERE id = {id}"`.
- No closing the connection inside `except`: only in `finally`.
- No opening a new connection per query in the same flow: reuse the same `connection` and pass it to each repository.
