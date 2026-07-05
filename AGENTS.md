# AGENTS.md — parking-hackathon-backend

> Operational guide for any agent working on this repository.
> Read this file before touching code. Open the `requirement-design-implementation` skill before implementing anything.

---

## 1. What is this project?

A **FastAPI** backend (Python 3.13) for a multi-tenant parking management system. An `Admin` user registers a parking, completes the onboarding, and from there manages floors, spots, plates, tariffs, entries, exits and payments. The `Cliente` role consumes a subset of endpoints (payment calculation and registration, payment methods listing).

**Visible product:** "Tracklinker / Parking Hackathon" (see `app/templates/welcome_mail.html`, `app/main.py:33`).

---

## 2. Stack and key dependencies

| Layer | Technology | Notes |
|---|---|---|
| HTTP | `fastapi` 0.136+ | Uvicorn as the ASGI server (`app/main.py:38`). |
| Validation | `pydantic` v2 + `pydantic-settings` | Settings in `app/core/config.py:1`. |
| DB | `mysql-connector-python` (sync driver) | Raw connection, no ORM. |
| Auth | `pyjwt` + `bcrypt` | JWT in HTTP-only cookies. |
| Cache / blacklist | `redis` (async) + `fastapi-limiter` | Initialized in `lifespan` (`app/main.py:24`). |
| Queue | `celery` with Redis broker | Async email. |
| Email | `fastapi-mail` | Templates in `app/templates/`. |
| Packaging | `uv` (see `uv.lock`, `DockerFile`) | Do not use `pip` directly. |

Python version: **3.13** (see `.python-version`, `pyproject.toml:6`).

---

## 3. Folder layout

```
app/
├── main.py                 # FastAPI app, lifespan, routers, CORS, health
├── core/                   # Config, DB, Redis, Mail, Celery, JWT, blacklist, errors
│   ├── config.py
│   ├── database.py
│   ├── redis.py
│   ├── cache.py
│   ├── celery_app.py
│   ├── mail.py
│   ├── security.py
│   ├── token_blacklist.py
│   └── exception.py
├── middlewares/            # verify_jwt, require_roles, require_onboarded
├── features/               # One module per domain (auth, users, parking, …)
│   └── <feature>/
│       ├── controllers/    # Handles HTTPException and shapes the response
│       ├── services/       # Business logic + transactions
│       ├── repositories/   # Raw SQL with mysql.connector
│       ├── routes/         # APIRouter, RateLimiter, middlewares
│       └── models/         # Pydantic: schemas (input) and responses (output)
├── tasks/                  # Celery tasks (email_tasks.py)
├── templates/              # HTML for emails
└── utils/                  # base_schema, logger, plate_formatter, round_to_50, date_formatter, safe_types
```

Each feature always follows **the same internal shape** — to add a new feature, see the `feature-scaffold` skill.

---

## 4. How to run

```bash
# Local
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Celery worker (in another terminal)
uv run celery -A app.core.celery_app.celery worker --loglevel=info

# Docker
docker build -t parking-backend .
```

Base URL: `http://localhost:8000`. Swagger: `/docs`. Healthchecks: `GET /` and `GET /ping-db`.

---

## 5. Quick conventions (details live in the skills)

- **Endpoints** `/api/<resource>` in plural, kebab-case in paths (`/complete-on-boarding`).
- **Languages**: code in English, **user-facing messages in Spanish** (e.g. `"La placa no puede estar vacía"`).
- **Logs**: `logger = get_logger("<module>.<layer>")` (see `app/utils/logger.py:1`).
- **Errors**: services raise `ServiceError` or return tuples `(error, data[, success, message])`. Controllers translate to `HTTPException`.
- **Transactions**: the `service` opens the connection with `get_connection()`, calls `commit()` at the end and `rollback()` in any `except`. The cursor is closed in `finally`.
- **Multi-tenant**: `parking_id` ALWAYS comes from the JWT (`payload["parking_id"]`); never from the body or the URL.
- **Roles**: `Admin` and `Cliente`. Apply with `Depends(require_roles([...]))` and `Depends(require_onboarded)` when applicable.
- **Plates**: always pass through `plate_formatter` (`app/utils/plate_formatter.py`).
- **User strings**: use `safe_str` / `safe_optional_str` / `safe_list_str` for validation + sanitization (`app/utils/safe_types.py`).
- **Money**: round up to the next multiple of 50 with `round_up_to_next_50` (`app/utils/round_to_50.py`).

---

## 6. Feature map

| Feature | Folder | Key endpoints | Minimum role |
|---|---|---|---|
| Auth | `app/features/auth` | `POST /api/auth/{login,register,refresh,logout,recover-password}`, `PUT /api/auth/complete-on-boarding` | public (login/register) |
| Users | `app/features/users` | `GET/POST/PUT /api/users/*` | Admin (some Admin+Cliente) |
| Parking (parking, plates, vehicle-types) | `app/features/parking` | `GET/POST /api/parking/*` | Admin |
| Floors | `app/features/floors` | `GET/POST/PUT/DELETE /api/floors/*` | any authenticated user |
| Spots | `app/features/spots` | `GET/POST/PUT/DELETE /api/spots/*` | any authenticated user |
| Entries | `app/features/entries` | `GET/POST /api/entries/*` | Admin (read) / Admin+Cliente (POST) |
| Exits | `app/features/exits` | `GET/POST /api/exits/*` | Admin (read) / authenticated (POST) |
| Tariffs | `app/features/tariffs` | `GET/POST/PUT/DELETE /api/tariffs/*` | Admin |
| Payments | `app/features/payments` | `GET/POST /api/payments/*` | Admin (read) / Cliente (`/calculate`, `/create`) |
| Countries | `app/features/countries` | `GET /api/countries` | Admin |

---

## 7. Available skills

Read the matching skill **before** touching that area:

| Skill | When to read it |
|---|---|
| `architecture` | To understand the layers, the request flow, where each file lives. |
| `code-conventions` | Before writing any new code (naming, returns, errors, logging, Pydantic). |
| `commits-and-prs` | Before running `git commit` or opening a PR. |
| `requirement-design-implementation` | **Always** before starting a new task. Defines the 3 phases. |
| `feature-scaffold` | When you are going to create a new feature/endpoint from scratch. |
| `auth-and-security` | If you touch login, JWT, cookies, blacklist, password, roles or onboarding. |
| `database-and-repository` | If you write SQL, open connections or touch transactions. |
| `api-layer` | If you add/modify routes, middlewares, rate limiting or the response shape. |
| `email-and-tasks` | If you touch Celery, emails or HTML templates. |

Each skill is invokable with `skill <name>` and is loaded as instructions in the current conversation.

---

## 8. Non-negotiable rules

1. **Do not** change the existing JSON response shape (it's a contract with the frontend `localhost:5173`).
2. **Do not** add dependencies to `pyproject.toml` without explicit permission.
3. **Do not** commit `.env`, credentials, or unjustified changes to `uv.lock`.
4. **Do not** break the `requirement-design-implementation` flow — always 3 phases, explicit output for each.
5. **Do not** skip the transaction: any write must go through `try/except/finally` with `commit/rollback/close`.
6. **Do not** use SQL with f-strings: always `%s` with `cursor.execute(query, values)`.
7. **Do not** trust a `parking_id` coming from the client: always from the JWT.

---

## 9. Pre-close checklist

- [ ] No stray `print(...)`: everything goes through `logger`.
- [ ] User-facing error messages in Spanish and friendly.
- [ ] Inputs validated with `safe_str` / pydantic, no raw strings.
- [ ] Connection closed in `finally`.
- [ ] Endpoint protected with `RateLimiter` and `require_roles` when applicable.
- [ ] `payload["parking_id"]` used in every query that touches parking data.
- [ ] Commit with conventional format (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`).

---

## 10. When something does not match this document

The code wins. If you find a divergence between this `AGENTS.md` (or a skill) and the actual code, **call it out in the PR** and update the matching skill. Documentation that does not reflect the code is worse than having none.
