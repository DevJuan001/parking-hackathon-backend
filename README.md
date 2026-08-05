# parking-hackathon-backend

Multi-tenant parking management backend. Three roles live in the same system: **Admin** registers and runs a parking, **Cliente** consumes a payment-only subset of the API, and **Maquina** is the kiosk role that creates entries and processes payments at the gate. The visible product is **Parking Hackathon** (see `app/main.py:33`).

Beyond the CRUD core, the system ships a **natural-language admin chatbot** built on Qdrant (RAG) plus an OpenAI-compatible LLM, so a parking operator can ask the system to do things instead of clicking through forms. Chatbot internals are documented in [`CHATBOT-ARCHITECTURE.md`](CHATBOT-ARCHITECTURE.md); this README only summarises them.

The frontend that consumes this API lives at `http://localhost:5173` and is CORS allow-listed in `app/main.py:52`.

---

## Quick path (5 minutes)

The shortest route from `git clone` to a running API:

1. **Clone and enter the project**
   ```bash
   git clone <repo-url> parking-hackathon-backend
   cd parking-hackathon-backend
   ```
2. **Install [`uv`](https://docs.astral.sh/uv/)** (skip if you already have it)
   ```bash
   # Windows (PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   # macOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Create `.env` from the template and fill it in**
   ```bash
   cp .env.example .env
   # then edit .env — see the "Configuration" section below
   ```
4. **Bring up MySQL 8 and Redis 7** (the easiest way is `docker compose -f docker-compose.dev.yml up -d db redis`; the full file also provisions Qdrant, the API, and a Celery worker)
5. **Install dependencies and run the API**
   ```bash
   uv sync
   uv run uvicorn app.main:app --reload --port 8000
   ```
6. **Smoke test**
   ```bash
   curl http://localhost:8000/        # -> {"message":"API funcionando"}
   curl http://localhost:8000/ping-db # -> {"status":"Conexion Exitosa a la base de datos"}
   ```
   Then open the interactive docs at <http://localhost:8000/docs>.

If any step fails, jump to the matching section below — "Running", "Configuration", or the `docker-and-deployment` skill at `.agents/docker-and-deployment/SKILL.md`.

---

## Stack and key dependencies

| Layer | Technology | Notes |
|---|---|---|
| HTTP | `fastapi` 0.136+ | Uvicorn as the ASGI server (`app/main.py:38`). |
| Validation | `pydantic` v2 + `pydantic-settings` | Settings in `app/core/config.py:1`. |
| Database | `mysql-connector-python` (sync driver) | Raw connection, no ORM. |
| Auth | `pyjwt` + `bcrypt` | JWT in HTTP-only cookies. |
| Cache / blacklist | `redis` (async) + `fastapi-limiter` | Initialized in `lifespan` (`app/main.py:24`). |
| Queue | `celery` with Redis broker | Async email. |
| Email | `fastapi-mail` | Templates in `app/templates/`. |
| Vector DB (chatbot) | `qdrant-client` + Qdrant 1.x | Only used when `CHATBOT_ENABLED=true`. |
| Embeddings (chatbot) | `sentence-transformers` (default `all-MiniLM-L6-v2`) | Local model; HF token optional. |
| LLM (chatbot) | `openai` Python SDK against an OpenAI-compatible endpoint | `AI_BASE_URL` points at Ollama, vLLM, OpenAI, etc. |
| OAuth | `authlib` | Google sign-in (optional). |
| Packaging | `uv` (see `uv.lock`, `DockerFile`) | **Do not** use `pip` directly. |

Python version: **3.13** (see `.python-version`, `pyproject.toml:6`).

---

## Requirements

- **Python 3.13** (already pinned via `.python-version` and `pyproject.toml`)
- **uv** for dependency management (installed above)
- **MySQL 8.x** — the schema lives in `database/parking_db_ddl.sql`, seed data in `database/parking_db_dml.sql`, and views in `database/parking_db_view.sql`
- **Redis 7.x** — used for both rate-limit state and the Celery broker

If you enable the chatbot (`CHATBOT_ENABLED=true` in `.env`) you also need:

- **Qdrant 1.x** (vector store for RAG)
- An **OpenAI-compatible LLM endpoint** — `AI_BASE_URL` + `AI_API_KEY` + `AI_MODEL` — Ollama with `qwen2.5` is the default tested target (see `CHATBOT-ARCHITECTURE.md`)

The full container stack (MySQL 8.0, Redis 7, Qdrant, API, Celery worker) is defined in `docker-compose.dev.yml`.

---

## Installation

Local install (recommended for day-to-day development):

```bash
uv sync                              # creates .venv and installs runtime deps
uv run uvicorn app.main:app --reload --port 8000
```

Containerized dev (recommended for a clean environment):

```bash
docker compose -f docker-compose.dev.yml up -d db redis qdrant
# then run the API locally with `uv run uvicorn ...`
# OR bring up the whole stack:
docker compose -f docker-compose.dev.yml up --build
```

> Note: `docker-compose.dev.yml` mounts **two** env files into the `api` and `celery_worker` services — `.env` (shared) and `.env.docker` (container-internal hostnames such as `db`, `redis`, `qdrant`). You will need to create `.env.docker` yourself the first time; the typical content is:
>
> ```ini
> DB_HOST=db
> REDIS_URL=redis://redis:6379/0
> QDRANT_HOST=qdrant
> QDRANT_PORT=6333
> ```

---

## Configuration

Every variable lives in `.env.example`. The table below groups them by concern and says what to put there in dev. **Do not** commit a real `.env` — it is already git-ignored.

### Database (MySQL 8)

| Variable | Purpose | Dev value | Where to get a real one |
|---|---|---|---|
| `DB_HOST` | MySQL hostname | `localhost` (or `db` inside Compose) | infra team |
| `DB_PORT` | MySQL port | `3306` | default |
| `DB_USER` | MySQL user | `root` (dev only) | infra team |
| `DB_PASSWORD` | MySQL password | local dev password | secret manager |
| `DB_NAME` | Schema name | `parking_db` | matches DDL file |

### Redis

| Variable | Purpose | Dev value |
|---|---|---|
| `REDIS_URL` | Connection string for rate-limiter + Celery broker + chatbot history | `redis://localhost:6379/0` |

### Environment

| Variable | Purpose | Dev value |
|---|---|---|
| `ENVIRONMENT` | Drives config branches | `development` |

### Auth / JWT

| Variable | Purpose | Dev value |
|---|---|---|
| `ACCESS_TOKEN_SECRET_KEY` | HMAC key for access tokens | generate one (`openssl rand -hex 32`) |
| `REFRESH_TOKEN_SECRET_KEY` | HMAC key for refresh tokens | **different** from the access key |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE` | Access-token lifetime in **minutes** | `60` |
| `REFRESH_TOKEN_EXPIRE` | Refresh-token lifetime in **days** | `7` |

### Email (FastAPI-Mail)

| Variable | Purpose | Dev value |
|---|---|---|
| `MAIL_USERNAME` | SMTP login | dev mailbox |
| `MAIL_PASSWORD` | SMTP password (use an app password) | dev secret |
| `MAIL_FROM` | `From:` header | dev mailbox |

For dev, a local SMTP catcher (MailHog, Mailpit) on port 1025 is fine.

### AI / LLM (chatbot)

| Variable | Purpose | Dev value |
|---|---|---|
| `AI_BASE_URL` | OpenAI-compatible base URL | `http://localhost:11434/v1` (Ollama) |
| `AI_API_KEY` | Bearer token for the LLM provider | `ollama` works for local Ollama |
| `AI_MODEL` | Model name | `qwen2.5` |
| `AI_MAX_TOKENS` | Response cap | `1024` |
| `AI_TEMPERATURE` | Sampling temperature (0.3 recommended to reduce hallucination) | `0.3` |

### Qdrant (chatbot only)

| Variable | Purpose | Dev value |
|---|---|---|
| `QDRANT_HOST` | Qdrant hostname | `localhost` (or `qdrant` in Compose) |
| `QDRANT_PORT` | Qdrant HTTP port | `6333` |

### Embeddings (chatbot only)

| Variable | Purpose | Dev value |
|---|---|---|
| `EMBEDDING_MODEL` | Sentence-Transformers model id | `all-MiniLM-L6-v2` |
| `HF_TOKEN` | Hugging Face token (only if pulling a gated model) | leave empty in dev |

### Google OAuth (optional)

| Variable | Purpose | Dev value |
|---|---|---|
| `GOOGLE_CLIENT_ID` | OAuth client id | Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret | Google Cloud Console |
| `GOOGLE_REDIRECT_URL` | OAuth callback URL | `http://localhost:5173` |

### Chatbot toggle

| Variable | Purpose | Dev value |
|---|---|---|
| `CHATBOT_ENABLED` | Master switch — when `false`, Qdrant is not initialised and the chatbot router is still mounted but returns 503 | `true` to test, `false` to skip the Qdrant/AI setup |

---

## Running

**Local API** (one terminal):

```bash
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

**Celery worker** (separate terminal, needed for async email):

```bash
uv run celery -A app.core.celery_app.celery worker --loglevel=info
```

**Containerized** (everything in one command):

```bash
docker compose -f docker-compose.dev.yml up --build
```

**Containerized production build** (just the API image):

```bash
docker build -t parking-backend .
```

Base URL: <http://localhost:8000>. Useful endpoints:

- `GET /` — service heartbeat
- `GET /ping-db` — DB connectivity check
- `GET /docs` — interactive Swagger UI
- `GET /redoc` — ReDoc UI

---

## Project structure

```
.
├── app/
│   ├── main.py                 # FastAPI app, lifespan, routers, CORS, health
│   ├── core/                   # Config, DB, Redis, Qdrant, Mail, Celery, JWT, blacklist, errors
│   ├── middlewares/            # verify_jwt, require_roles, require_onboarded
│   ├── features/               # One module per domain (see Feature map below)
│   │   └── <feature>/
│   │       ├── controllers/    # HTTPException handling + response shape
│   │       ├── services/       # Business logic + transactions
│   │       ├── repositories/   # Raw SQL with mysql.connector
│   │       ├── routes/         # APIRouter, RateLimiter, middlewares
│   │       └── models/         # Pydantic: input schemas + response models
│   ├── tasks/                  # Celery tasks (email_tasks.py)
│   ├── templates/              # HTML for emails
│   └── utils/                  # base_schema, logger, plate_formatter, round_to_50, date_formatter, safe_types
├── database/                   # SQL DDL/DML/views — schema source of truth (no Alembic)
├── .agents/                    # 17 LLM skills — see "Skills for agents"
├── .github/                    # PR template
├── AGENTS.md                   # Operational guide for AI agents
├── CHATBOT-ARCHITECTURE.md     # Chatbot design (305 lines)
├── docker-compose.dev.yml      # Local container stack (db, redis, qdrant, api, celery_worker)
├── DockerFile                  # Production image (uv + python:3.13-slim)
├── pyproject.toml              # Project metadata + dependencies (managed by uv)
├── uv.lock                     # Lockfile
└── .python-version             # Pinned to 3.13
```

The chatbot feature (`app/features/chatbot/`) is the only feature with extra directories on top of the standard shape — it adds `prompts/` (LLM system prompt and RAG context) and `tools/` (the 20 tool handlers the LLM can call). See `CHATBOT-ARCHITECTURE.md` for the full picture.

---

## Feature map

Twelve domain features, each one self-contained under `app/features/<name>/`. Minimum roles reflect the JWT-issued claims; the list is enforced by `Depends(require_roles([...]))` on each route.

| Feature | Folder | Key endpoints | Minimum role |
|---|---|---|---|
| Auth | `app/features/auth` | `POST /api/auth/{login,register,refresh,logout,recover-password}`, `PUT /api/auth/complete-on-boarding` | public (login/register) |
| Users | `app/features/users` | `GET/POST/PUT /api/users/*` | Admin (some Admin+Cliente) |
| Parking (parking, plates, vehicle-types) | `app/features/parking` | `GET/POST /api/parking/*` | Admin |
| Floors | `app/features/floors` | `GET/POST/PUT/DELETE /api/floors/*` | any authenticated user |
| Spots | `app/features/spots` | `GET/POST/PUT/DELETE /api/spots/*` | any authenticated user |
| Entries | `app/features/entries` | `GET/POST /api/entries/*` | Admin (read) / Admin+Maquina (POST) |
| Exits | `app/features/exits` | `GET/POST /api/exits/*` | Admin (read) / authenticated (POST) |
| Tariffs | `app/features/tariffs` | `GET/POST/PUT/DELETE /api/tariffs/*` | Admin |
| Payments | `app/features/payments` | `GET/POST /api/payments/*` | Admin (read) / Maquina (`/calculate`, `/create`, `/payment-methods`) |
| Reservations | `app/features/reservations` | `GET/POST /api/reservations/*` | Admin (read/create-for-user) / Cliente (`/create-self`) |
| Countries | `app/features/countries` | `GET /api/countries` | Admin |
| Chatbot | `app/features/chatbot` | `POST /api/chatbot/ask` (and admin tools) | Admin |

---

## Skills for agents

The repo ships **17 skills** under `.agents/`. Load the matching skill **before** touching the area it covers. Each entry is the `description:` frontmatter verbatim — treat it as the trigger phrase.

| Skill | Load it when… |
|---|---|
| `requirement-design-implementation` | Mandatory 3-phase flow every task must follow in parking-hackathon-backend: Requirements → Design → Implementation. Load before starting any task. |
| `architecture` | Project structure, layers and request flow for the parking-hackathon-backend. Read this before changing where a file lives or adding a new module. |
| `code-conventions` | Naming, returns, error handling, logging and Pydantic patterns used across the parking-hackathon-backend. Apply on every new or changed file. |
| `feature-scaffold` | How to add a new feature module to parking-hackathon-backend following the routes → controllers → services → repositories convention. Load when creating a new endpoint or domain. |
| `api-layer` | Routes, middlewares, rate limiting, response shapes and CORS for parking-hackathon-backend. Load when adding/changing endpoints, middlewares, or response formats. |
| `auth-and-security` | JWT, cookies, token blacklist, bcrypt password hashing, roles and onboarding in parking-hackathon-backend. Load when touching login, /api/auth/*, password, roles or onboarding. |
| `database-and-repository` | How database access works in parking-hackathon-backend: connection lifecycle, transactions, SQL style, and repository rules. Load before writing any SQL or touching transactions. |
| `database-migrations` | DDL/DML workflow for parking-hackathon-backend. Load when adding columns, tables, indexes, or seed data. Note: the project does NOT use Alembic — schema lives in `database/parking_db_ddl.sql`. |
| `config-and-settings` | Environment variables and pydantic-settings configuration in parking-hackathon-backend. Load when adding a new env var, debugging settings, or reading `.env.example`. |
| `caching` | Redis-backed caching helpers in parking-hackathon-backend (`app/core/cache.py`). Load when deciding whether to cache an endpoint or invalidating a cache. Note: the cache API is currently ORPHANED — no callers in the repo. |
| `pagination` | Pagination pattern (per_page + page with LIMIT/OFFSET) used in parking-hackathon-backend listings. Load when adding a paginated endpoint or modifying an existing one. |
| `logging-conventions` | Logging conventions for parking-hackathon-backend: levels by layer, what to never log, and the standard error format. Load when adding log statements or auditing log output. |
| `email-and-tasks` | Celery tasks and FastAPI-Mail templates for parking-hackathon-backend. Load when adding async emails, Celery tasks or modifying HTML templates. |
| `chatbot` | AI-powered admin chatbot (Qdrant RAG + OpenAI-compatible LLM + Redis history). Load when touching the chatbot feature, adding tools, modifying the system prompt, the intent classifier, or knowledge generation. |
| `tool-registry` | LLM tool registration contract for the chatbot (app/features/chatbot/services/tool_registry.py). Load when adding a new tool, modifying tool access by role, or changing the tool dispatch flow. |
| `commits-and-prs` | Conventional commits, branching and PR conventions for parking-hackathon-backend. Load before `git commit` or `gh pr create`. |
| `docker-and-deployment` | Docker setup for parking-hackathon-backend. Load when touching the DockerFile, docker-compose, or deploying locally with containers. |

> Note: `AGENTS.md` section 7 lists only 9 of these — that section is out of date. The canonical list is the filesystem under `.agents/`. When `AGENTS.md` and the skills disagree, **the skills win**; open a PR to update `AGENTS.md` so the next agent does not get confused.

---

## Multi-tenancy and security

**Multi-tenancy is enforced at the token level.** Every query that touches parking-scoped data filters by `parking_id` taken **from the JWT payload** (`payload["parking_id"]`), never from the request body, never from a path parameter, never from a query string. A client cannot impersonate another tenant by tampering with input. This is rule #7 of the non-negotiables in `AGENTS.md` and the reason every `service`/`repository` accepts the parking id through a `Depends(get_current_parking_id)`-style resolver rather than reading it from the route.

**Authentication uses HTTP-only cookies.** The access token and refresh token are both delivered as `HttpOnly` cookies (see `app/core/security.py`), so JavaScript on `localhost:5173` cannot exfiltrate them. Logout calls the token-blacklist module which marks the JTI in Redis until the access token would have expired. The `bcrypt` password hash and the JWT signing keys are read from `.env` (see the Auth/JWT row in Configuration).

**Rate limiting and CORS.** `fastapi-limiter` is initialised against Redis in the `lifespan` and applied to every mutating endpoint via `RateLimiter(...)` in the route file. CORS is restricted to `http://localhost:5173` in `app/main.py:52`; do **not** widen it without a security review. The `commits-and-prs` skill has the PR template and the `auth-and-security` skill is the single source of truth for cookie/JWT/blacklist/onboarding mechanics.

**Transactions and SQL are non-negotiable.** Every write goes through the pattern `get_connection() → cursor.execute(query, %s params) → commit() on success, rollback() on any exception, cursor/connection closed in finally`. SQL must use `%s` parameter substitution — never f-strings. The `database-and-repository` skill spells it out.

---

## Conventions

A short list. Details live in the matching skill (`code-conventions`, `logging-conventions`, `auth-and-security`).

- **Endpoints** are `/api/<resource>` in plural, kebab-case in paths (`/complete-on-boarding`).
- **Languages** — code (identifiers, comments, log messages) is in English; **user-facing error messages and UI copy are in Spanish** (e.g. `"La placa no puede estar vacía"`).
- **Logging** — every module does `logger = get_logger("<module>.<layer>")` from `app/utils/logger.py:1`. No `print(...)` in committed code.
- **Errors** — services raise `ServiceError` or return `(error, data[, success, message])` tuples; controllers translate to `HTTPException`. Never leak internal exceptions to the client.
- **Transactions** — service opens the connection, commits at the end, rolls back on any `except`, closes in `finally`.
- **Multi-tenant** — `parking_id` always from the JWT.
- **Roles** — apply with `Depends(require_roles([...]))`; for Admin-only mutations also `Depends(require_onboarded)`.
- **Plates** — always pass through `plate_formatter` (`app/utils/plate_formatter.py`).
- **User strings** — validate with `safe_str` / `safe_optional_str` / `safe_list_str` (`app/utils/safe_types.py`); never trust raw `str` in a service.
- **Money** — round up to the next multiple of 50 with `round_up_to_next_50` (`app/utils/round_to_50.py`).

---

## Pre-commit checklist

Run through this before opening a PR (mirrors `AGENTS.md` section 9):

- [ ] No stray `print(...)` — everything goes through `logger`.
- [ ] User-facing error messages are in Spanish and friendly.
- [ ] Inputs are validated with `safe_str` / pydantic; no raw strings in services.
- [ ] Database connection closed in `finally`.
- [ ] Endpoint protected with `RateLimiter` and `require_roles` where applicable.
- [ ] `payload["parking_id"]` used in every query that touches parking data.
- [ ] Commit message uses the conventional format (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`).
- [ ] No changes to the JSON response shape (it is a contract with `localhost:5173`).

---

## Contributing

1. **Read `AGENTS.md` first.** It is the operational guide for both humans and AI agents and overrides this README if they ever disagree.
2. **Follow the 3-phase flow.** Every task goes through **Requirements → Design → Implementation** with explicit output for each. The `requirement-design-implementation` skill is mandatory before you start coding.
3. **Branch naming** — `feat/<short-slug>`, `fix/<short-slug>`, `chore/<short-slug>`. Match the work-unit in the branch name.
4. **Commit messages** — Conventional Commits. One logical change per commit. Read the `commits-and-prs` skill before `git commit`.
5. **PR template** — fill in `.github/PULL_REQUEST_TEMPLATE.md`. Group changes by section (Project setup, Core, Middlewares, Features, Utils, Tasks, Docs). Reviewers will look there first.
6. **Do not** add dependencies to `pyproject.toml` without explicit approval, and **do not** hand-edit `uv.lock` — run `uv add …` instead.
7. **Do not** commit `.env` or any other secret. The chatbot tools may dump AI responses to logs; never log API keys, JWTs, or full request bodies.

When documentation drifts from code, open a follow-up PR to update it — the `code wins` rule from `AGENTS.md` section 10 is the standard.

---

## Related docs

- [`AGENTS.md`](AGENTS.md) — operational guide for any agent (or human) working on the repo. **Read this first.**
- [`CHATBOT-ARCHITECTURE.md`](CHATBOT-ARCHITECTURE.md) — full chatbot design (intent classifier, RAG, tool registry, snapshot/context builder, 305 lines).
- [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) — the PR template used by reviewers.
- `.agents/<skill>/SKILL.md` — 17 specialized skills. See the **Skills for agents** section for the full list.
