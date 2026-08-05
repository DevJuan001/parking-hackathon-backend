---
name: config-and-settings
description: Environment variables and pydantic-settings configuration in parking-hackathon-backend. Load when adding a new env var, debugging settings, or reading `.env.example`.
---

# Config & settings

## Where it lives

`app/core/config.py` — a `pydantic_settings.BaseSettings` subclass that:

- Loads from a `.env` file in the repo root (`env_file = ".env"`).
- Validates types at import time — **the process fails to start if a required var is missing**.
- Exports a singleton: `from app.core.config import settings`.

```python
from app.core.config import settings

print(settings.AI_MODEL)        # str
print(settings.AI_TEMPERATURE)   # float, default 0.3
print(settings.CHATBOT_ENABLED) # bool, default True
```

Pydantic coerces strings to the declared type (e.g. `int`, `bool`, `EmailStr`).

## Pattern — adding a new env var

1. Add the field to `Settings` in `app/core/config.py` with a type and (if optional) a default.
2. Add the var to `.env.example` (or the project doc that lists env vars) with a short comment.
3. Read it via `settings.<NAME>` — never `os.environ["..."]`.

```python
# app/core/config.py
class Settings(BaseSettings):
    # ...existing fields...
    MY_NEW_VAR: str                # required, app fails to start if missing
    MY_OPTIONAL_VAR: int = 30      # optional, default 30
    MY_BOOL: bool = False          # pydantic accepts "true"/"false"/"1"/"0"
```

## Env var groups

The repo groups vars by domain. Treat the table as the canonical list — `app/core/config.py` is the actual source of truth and `.env.example` is the user-facing template.

### Database (MySQL)

| Var | Type | Required | Notes |
|---|---|---|---|
| `DB_HOST` | str | yes | |
| `DB_PORT` | int | yes | |
| `DB_USER` | str | yes | |
| `DB_PASSWORD` | str | yes | |
| `DB_NAME` | str | yes | |

These map to `get_connection()` in `app/core/database.py` with `charset="utf8mb4"` and `collation="utf8mb4_unicode_ci"` (see `database-and-repository`).

### Redis

| Var | Type | Required | Notes |
|---|---|---|---|
| `REDIS_URL` | str | yes | Broker for Celery and store for `FastAPILimiter` and chatbot history. |

### Auth (JWT)

| Var | Type | Required | Notes |
|---|---|---|---|
| `ACCESS_TOKEN_SECRET_KEY` | str | yes | Sign access tokens. |
| `REFRESH_TOKEN_SECRET_KEY` | str | yes | Sign refresh tokens. |
| `ALGORITHM` | str | yes | E.g. `HS256`. |
| `ACCESS_TOKEN_EXPIRE` | int | yes | In **minutes**. |
| `REFRESH_TOKEN_EXPIRE` | int | yes | In **days**. |

### Mail (Gmail STARTTLS)

| Var | Type | Required | Notes |
|---|---|---|---|
| `MAIL_USERNAME` | EmailStr | yes | Sender. |
| `MAIL_PASSWORD` | str | yes | Gmail **app password** (not the account password). |
| `MAIL_FROM` | EmailStr | yes | Usually equal to `MAIL_USERNAME`. |
| `MAIL_PORT` | int | no (default `587`) | SMTP submission port. Use `587` with `MAIL_STARTTLS=True` (recommended) or `465` with `MAIL_SSL_TLS=True`. |
| `MAIL_SERVER` | str | no (default `smtp.gmail.com`) | SMTP hostname. Override for SendGrid, AWS SES, Mailgun, etc. |
| `MAIL_STARTTLS` | bool | no (default `True`) | Upgrade the plain SMTP connection to TLS via the `STARTTLS` command. Recommended with port `587`. |
| `MAIL_SSL_TLS` | bool | no (default `False`) | Wrap the whole SMTP session in TLS from byte 0 (like HTTPS). Use only with port `465`. Mutually exclusive with `MAIL_STARTTLS`. |

All `MAIL_*` vars are loaded by `pydantic-settings` into `Settings` (`app/core/config.py:28-34`) and consumed by `ConnectionConfig` in `app/core/mail.py:5-11`.

### Chatbot (LLM)

| Var | Type | Required | Default |
|---|---|---|---|
| `AI_API_KEY` | str | yes | — |
| `AI_BASE_URL` | str | yes | — (OpenAI-compatible: hosted or local) |
| `AI_MODEL` | str | yes | — |
| `AI_MAX_TOKENS` | int | no | `1024` |
| `AI_TEMPERATURE` | float | no | `0.3` |
| `CHATBOT_ENABLED` | bool | no | `True` |

### Qdrant (RAG vector store)

| Var | Type | Required | Default |
|---|---|---|---|
| `QDRANT_HOST` | str | yes (if chatbot on) | — |
| `QDRANT_PORT` | int | yes (if chatbot on) | — |

### Embeddings

| Var | Type | Required | Default |
|---|---|---|---|
| `EMBEDDING_MODEL` | str | yes (if chatbot on) | — (typical: `all-MiniLM-L6-v2`) |
| `HF_TOKEN` | str | yes (pydantic requires it; the app fails to start without it) | — |

The collection `parking_knowledge` is hard-coded to **size 384, distance COSINE** in `app/core/qdrant.py`. If you change `EMBEDDING_MODEL` to one with a different output size, the Qdrant upsert will fail.

### Google OAuth

| Var | Type | Required | Notes |
|---|---|---|---|
| `GOOGLE_CLIENT_ID` | str | yes | OAuth client id from Google Cloud Console. Read by `app/core/oauth.py:9`. |
| `GOOGLE_CLIENT_SECRET` | str | yes | OAuth client secret. Read by `app/core/oauth.py:10`. |
| `GOOGLE_REDIRECT_URL` | str | yes | E.g. `http://localhost:8000/api/auth/google-callback`. Used as `redirect_uri` in `authlib` and by the `POST /api/auth/google-login` flow (`app/features/auth/services/auth_service.py:95`). |

All three are declared as required `str` in `app/core/config.py:45-47` (no default), so the process fails to start if any is missing — even for users who never hit the Google login route. The `OAUTH_DISCOVERY_URL` (`https://accounts.google.com/.well-known/openid-configuration`) is hard-coded in `app/core/oauth.py:11`, not env-driven.

### Celery

Celery currently uses `REDIS_URL` for both broker and result backend. If you add separate URLs, they go here:

| Var | Type | Required | Notes |
|---|---|---|---|
| `CELERY_BROKER_URL` | str | no | Currently reuses `REDIS_URL`. |
| `CELERY_RESULT_BACKEND` | str | no | Currently reuses `REDIS_URL`. |

### Misc

| Var | Type | Required | Notes |
|---|---|---|---|
| `ENVIRONMENT` | str | yes | E.g. `development`, `production`. Used for logging and conditional behavior. |
| `FRONTEND_URL` | str | yes | The CORS origin (`http://localhost:5173` in dev) lives in `app/main.py` directly. Add a new var here only if you want to make CORS configurable. |

## Required vs optional summary

Required (the app **fails to start** without them): `DB_*`, `REDIS_URL`, `ENVIRONMENT`, `ACCESS_TOKEN_SECRET_KEY`, `REFRESH_TOKEN_SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE`, `REFRESH_TOKEN_EXPIRE`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`, `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL`, `HF_TOKEN`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URL`.

Optional with defaults: `AI_MAX_TOKENS`, `AI_TEMPERATURE`, `CHATBOT_ENABLED`, `QDRANT_HOST`, `QDRANT_PORT`, `EMBEDDING_MODEL`.

If the chatbot is off (`CHATBOT_ENABLED=False`), Qdrant and embedding vars can be empty (the client is not initialized).

## Anti-patterns

- **Hardcoding values in code.** A constant like `127.0.0.1` or `30 / 60` belongs in `.env` (or in a single constant module if truly global).
- **Reading env vars with `os.environ` instead of `settings`.** Bypasses pydantic validation and the startup check.
- **Adding a var without updating `.env.example`.** Anyone cloning the repo will hit the startup error without a hint.
- **Storing secrets in `Settings` defaults.** Pydantic only validates type — a default like `AI_API_KEY: str = "demo"` is silently accepted.
- **Sharing a single `Settings()` instance across tests without resetting it.** The pydantic `BaseSettings` instance is read once; if you `monkeypatch.setenv` in a test, the existing `settings` does not pick it up. Re-import the module or patch `settings` directly.
- **Forgetting the embedding dimension.** The Qdrant collection is hard-coded to 384. Changing `EMBEDDING_MODEL` without coordinating the vector size is a runtime failure.

## Common errors

- `pydantic.ValidationError: ... field required` at import → a required var is missing in `.env`.
- `email-validator` not installed and `EmailStr` raises → `pip install email-validator` (it is a transitive dep of `pydantic[email]`).
- `CHATBOT_ENABLED=True` but Qdrant is unreachable → `app/main.py:33` raises at startup. Set `CHATBOT_ENABLED=False` if you don't need the chatbot.
