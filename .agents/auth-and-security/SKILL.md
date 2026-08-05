---
name: auth-and-security
description: JWT, cookies, token blacklist, bcrypt password hashing, roles and onboarding in parking-hackathon-backend. Load when touching login, /api/auth/*, password, roles or onboarding.
---

# Auth & security

## Authentication flow

```
register (public)
  → creates USERS with bcrypt password, role_id=1 (Admin), onboarding_completed=False
  → issues access + refresh tokens with onboarding_completed=False
  → set_auth_cookies(response, access, refresh)

complete-on-boarding (Admin, authenticated)
  → creates parking, default floor ("Piso 1")
  → updates users with personal data, parking_id, onboarding_completed=1
  → issues new tokens with onboarding_completed=True
  → enqueues send_welcome_registration_email

login (public)
  → finds user by email
  → verify_password
  → issues tokens with the user's role
  → set_auth_cookies

refresh (public, reads refresh_token cookie)
  → decodes refresh
  → blacklists the old refresh with its remaining TTL
  → issues new access + refresh
  → set_auth_cookies

logout (reads both cookies)
  → deletes cookies
  → blacklists access + refresh with their remaining TTL

recover-password (public)
  → if the email exists, enqueues recovery_password_email (always generic response to avoid leaking existence)
```

## Google OAuth login

A second login path exists for users who authenticate through Google instead of email/password.

- `POST /api/auth/google-login` (`app/features/auth/routes/auth_routes.py:34-41`) is rate-limited to **10/min** (`auth_routes.py:37`) and takes `GoogleLoginModelSchema` with a single `code: str` field (`app/features/auth/models/auth_schema.py:12-13`, singular filename).
- The OAuth client lives in `app/core/oauth.py` — `authlib.starlette_client.OAuth` registered with `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` from `Settings`, discovery URL `https://accounts.google.com/.well-known/openid-configuration`, scope `openid email profile` (`app/core/oauth.py:7-12`).
- `USERS.password` is `TEXT NULL` (`database/parking_db_ddl.sql:41`) — Google users have no password; `AuthService.google_login` creates a shell user with `hash_password=None` (`app/features/auth/services/auth_service.py:122-137`).
- **Anti-pattern — do not fix in passing:** `AuthService.recover_password` wraps the body in `try/except: pass` (`app/features/auth/services/auth_service.py:505-515`). DB outages, Celery outages, malformed emails — every failure is silently swallowed and the client still sees `"Correo enviado correctamente"`. Surface it in the PR so the team can decide between logging, structured retry, or a real 5xx.

## Cookies (`app/core/security.py:set_auth_cookies`)

- `httponly=True` always.
- `secure=True` only in `ENVIRONMENT == "production"`.
- `samesite="none"` in production, `"lax"` in dev.
- `access_token`: `path="/"`, `max_age = ACCESS_TOKEN_EXPIRE * 60` (minutes → seconds).
- `refresh_token`: `path="/api/auth/refresh"`, `max_age = REFRESH_TOKEN_EXPIRE * 86400` (days → seconds).

## JWT

`app/core/security.py:create_access_token`:

- `to_encode["sub"] = str(to_encode["sub"])` — the subject is always a string.
- `expire` defaults to `now + ACCESS_TOKEN_EXPIRE` minutes. Override with `expires_delta=timedelta(...)`.
- Typical payload: `{"sub": str(user_id), "role": role_name, "onboarding_completed": bool}`.
- Signed with `settings.ACCESS_TOKEN_SECRET_KEY` and `settings.ALGORITHM`.

`create_refresh_token`: just adds `exp = now + REFRESH_TOKEN_EXPIRE` days. Same `sub`, `role`, `onboarding_completed`.

## `verify_jwt` — `app/middlewares/jwt_middleware.py`

Reads the `access_token` cookie, decodes, and returns:

```python
{
    "user_id": str,
    "role": str,
    "parking_id": int | None,  # None if onboarding not completed
    "onboarding_completed": bool
}
```

`verify_jwt` reads `parking_id`, `onboarding_completed` and `role` from the JWT payload (the payload is cryptographically signed with `settings.ACCESS_TOKEN_SECRET_KEY`; the DB is not consulted per request).

Important:

- If the token has no `sub` or `role` → 401.
- Any `PyJWTError` → 401 "Token inválido o expirado".

## Roles and onboarding

There are three roles in the system: `Admin`, `Maquina`, and `Cliente`.

- `Admin` — the parking owner / staff. Manages floors, spots, plates, tariffs, entries, exits, payments, and users. Creates reservations on behalf of users.
- `Maquina` — machine-driven role (e.g. kiosks, plate-recognition cameras, self-service machines). Performs entry creation, payment calculation and registration, payment methods listing, and self-reservations via the API. The role is referenced in the JWT as `Maquina` (a string) and is stored in `ROLES` as a separate role_id.
- `Cliente` — end-user / driver. Consumes a subset of endpoints (self-reservations) plus any future driver-facing flows.

- `require_roles(["Admin"])`, `["Admin", "Maquina"]`, `["Admin", "Cliente"]`, or `["Admin", "Maquina", "Cliente"]` — rejects with 403 if the role is not in the list.
- `require_onboarded` — rejects with 403 "Debes completar el onboarding…" if `payload["onboarding_completed"]` is false.
- For public routes (login, register, refresh, recover-password) **do not** apply `verify_jwt`.

## Blacklist (`app/core/token_blacklist.py`)

- Storage: Redis with a single prefix `blacklist:access_token:` (`app/core/token_blacklist.py:9` — `BLACKLIST_PREFIX`). Both access and refresh tokens share the same prefix; the module does **not** distinguish them.
- Value: `"1"`.
- TTL: what is left on the token at the moment of blacklisting. Calculated with `get_token_remaining_ttl(token)` which decodes **without verifying the signature** and reads `payload["exp"]`.
- `is_blacklisted(token)` will be used by future middlewares (today only writes happen, no blocking in the current flow — it is still the source of truth for invalidation).
- Called in `refresh_tokens` and `logout`. If the Redis write fails, a warning is logged but the operation is **not** broken (best effort).

## Passwords

- Hash: `bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12)).decode("utf-8")`.
- Verify: `bcrypt.checkpw(password_bytes, hashed_bytes)` (helper in `security.py:verify_password`).
- Temporary generation: `generate_temporal_password(length=12)` (uppercase + lowercase + digit guaranteed, symbols `!@#$%&*`, shuffled with `SystemRandom().shuffle`).
- In the DB, the already-hashed passwords are stored as `str` (bcrypt text). The column is `password` in `USERS`.

## Cookie testing (curl)

```bash
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"secret123"}'

curl -b cookies.txt http://localhost:8000/api/users/me
```

## Sensitive changes — checklist

- If you change the JWT payload format, remember there are tokens in flight. Decide whether you break compatibility or migrate.
- If you change the cookie names, update `set_auth_cookies` and `delete_cookie` (logout) in the same PR.
- If you add a new payload field, pass it through `refresh_tokens` too so it is preserved.
- If you touch `verify_jwt`, remember the payload is signed with `settings.ACCESS_TOKEN_SECRET_KEY` — any change to the JWT shape will break tokens already in flight.

## User-facing error messages (auth)

- "¡Parece que aún no tienes cuenta! Regístrate en unos segundos y empieza a usar la app." — login, user not found (`app/features/auth/services/auth_service.py:43`).
- "Verifica que tus credenciales esten escritas correctamente e intentalo nuevamente" — login, `verify_password` failed (`app/features/auth/services/auth_service.py:49`).
- "Las contraseñas no coinciden" — register, `password != repeat_password` (`app/features/auth/services/auth_service.py:188`).
- "Lo sentimos por el momento no podemos crear tu cuenta, por favor intentalo nuevamente más tarde" — register, email already exists (`app/features/auth/services/auth_service.py:200`).
- "Refresh token no encontrado" — refresh, no `refresh_token` cookie (`app/features/auth/services/auth_service.py:399`).
- "Refresh token inválido" — refresh, no `sub` in the decoded payload (`app/features/auth/services/auth_service.py:412`).
- "Refresh token expirado o inválido" — refresh, `PyJWTError` (`app/features/auth/services/auth_service.py:447`).
- "Correo enviado correctamente" — `recover-password` always returns this regardless of whether the email exists; anti-enumeration pattern (`app/features/auth/services/auth_service.py:517`). See the `try/except: pass` warning above.
- "El usuario ya completó el onboarding" — `complete-on-boarding` called twice (`app/features/auth/services/auth_service.py:292`).
- "No se pudo obtener la información del usuario de Google" — google-login, empty `user_info` from Google (`app/features/auth/services/auth_service.py:105`).
- "Google no proporcionó un email" — google-login, no `email` claim in `user_info` (`app/features/auth/services/auth_service.py:114`).
- "Token inválido o expirado" — `verify_jwt` (`app/middlewares/jwt_middleware.py:11`).
- "No puedes realizar esta acción" — `require_roles` (`app/middlewares/roles_middleware.py:35`).
- "Debes completar el onboarding para acceder a este recurso" — `require_onboarded` (`app/middlewares/onboarding_middleware.py:10`).
