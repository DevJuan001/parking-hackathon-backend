---
name: logging-conventions
description: Logging conventions for parking-hackathon-backend: levels by layer, what to never log, and the standard error format. Load when adding log statements or auditing log output.
---

# Logging conventions

## Logger

`app/utils/logger.py` exposes a single helper:

```python
from app.utils.logger import get_logger

logger = get_logger("module.layer")
```

It returns a stdlib `logging.Logger` with a `StreamHandler` to stdout, format `%(asctime)s | %(levelname)s | %(name)s | %(message)s`, and `DEBUG` level. Handlers are added only once per name (idempotent), so multiple imports of the same module share one logger.

Naming convention: `<domain>.<layer>`. Examples already in the repo:

- `entries.repository`, `entries.service`
- `chatbot.rag_service`, `chatbot.intent_classifier`, `chatbot.tool_registry`
- `core.qdrant`, `core.celery_app` (the Celery logger inherits from its own name)

## Levels by layer

| Layer | Level | When |
|---|---|---|
| `repository` | `ERROR` | In the `except Exception as e:` block, always with `exc_info=True`. |
| `service` | `ERROR` | Same — the `except` block, with `exc_info=True`. |
| `service` | `WARNING` | Soft failures that the caller should know about (e.g. `ConversationService` couldn't load history). |
| `controller` | (none) | Errors flow through `HTTPException`. No logger. |
| `route` | (none) | No logger. |
| `chatbot.tool_registry` | `INFO` | One line per tool call: `logger.info("Tool llamado: %s | args: %s | usuario: %s", ...)`. |
| `chatbot.intent_classifier` | `WARNING` | On injection match: `logger.warning("Intento de inyección detectado: %s", message[:100])`. |
| `chatbot.rag_service` | `WARNING` | Soft failures (history unavailable, tool calls not supported by model). |

## Standard error format

```python
try:
    cursor.execute(query, values)
    results = cursor.fetchall()
    return None, data
except Exception as e:
    logger.error("Error en <method_name>: %s", e, exc_info=True)
    return "Mensaje en español para el usuario", None
finally:
    cursor.close()
```

Rules:

- **Lazy formatting**: pass the format string and the value as args (`logger.error("...: %s", e, exc_info=True)`). Do not pre-format with f-strings — it allocates the message even if the level is filtered.
- **Always include `exc_info=True`** on `ERROR` so the stacktrace is attached.
- **The first arg is a human-readable tag** for the log search: `"Error en find_all_entries: %s"`, not `"find_all_entries failed: %s"`. Searchable in Splunk / Loki.
- **The user-facing message in the return tuple is in Spanish** and **does not include internals**. The log has the internals; the user has a friendly message.

## NEVER log

- **Passwords** (raw, hashed, or temporary).
- **JWT tokens** (access or refresh, raw or partially redacted).
- **bcrypt hashes**.
- **Email contents** (they may include temporary passwords for newly-created users, per `app/templates/welcome_mail.html`).
- **PII beyond `user_id` / `parking_id`**: no emails, plate numbers, phone numbers, addresses, full names. The correlation in logs should be by ID.
- **Qdrant payloads verbatim** if they include user-facing data — log the `chunk_id` and `score`, not the text.

If you need to log a value for debugging, log the **length** or the **type**, not the content.

## No `print(...)` in production code

The repo does not have `print(...)` in `app/`. A reviewer or linter should reject any PR that adds one. Use `logger.info` (or higher) instead.

If a script needs stdout (a Celery worker, a one-off migration), it can use `print` — but Celery's own logging covers worker output, so prefer `logger.info`.

## Anti-patterns

- `logger.info` with sensitive data ("User logged in: %s", user.email) — leaks PII.
- `logger.info` for an error condition — the level is wrong; use `logger.error` with `exc_info=True`.
- Swallowing exceptions silently: `except Exception: pass`. Always log before returning the error tuple.
- Logging the same error twice (once in the service, once in the repository). The service is the right place; the repository should `return` the error tuple and let the service log it.
- Using `exc_info=False` to "save space" on `ERROR` — the stacktrace is the most useful part of the log line.
- Logging in a tight loop (e.g. per row in a `for item in results`). Aggregate instead: `logger.info("Processed %d rows", len(results))`.

## Common errors

- `KeyError: 'message'` from a structured log handler → you used `f"Error: {e}"` instead of `"Error: %s", e`. Switch to lazy formatting.
- Duplicate log lines for the same event → the logger was created with `propagate=True` (default) and a parent logger also has a handler. Either disable propagation or pick a unique logger name.
- The log line is missing the traceback → `exc_info=True` is missing. Add it.

## Required environment variables

None. Logging is stdout-only and uses stdlib.
