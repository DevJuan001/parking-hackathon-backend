---
name: email-and-tasks
description: Celery tasks and FastAPI-Mail templates for parking-hackathon-backend. Load when adding async emails, Celery tasks or modifying HTML templates.
---

# Email & Celery tasks

## Architecture

```
service  →  <task>.delay(...)   (enqueues in Redis broker)
                                       │
                                       ▼
                              celery worker  (separate process)
                                       │
                                       ▼
                              FastMail.send_message(...)
                                       │
                                       ▼
                              SMTP (Gmail STARTTLS :587)
```

- **Broker** and **backend** are both Redis (`settings.REDIS_URL`).
- **Worker** is started with: `uv run celery -A app.core.celery_app.celery worker --loglevel=info`.
- **Serializer**: JSON, `timezone="America/Bogota"`, `enable_utc=True`.

## Where everything lives

- `app/core/celery_app.py` — `celery = Celery("worker", broker=…, backend=…, include=["app.tasks.email_tasks"])`.
- `app/core/mail.py` — `ConnectionConfig` with `MAIL_PORT=587`, `MAIL_SERVER="smtp.gmail.com"`, `MAIL_STARTTLS=True`, `MAIL_SSL_TLS=False`, `TEMPLATE_FOLDER="app/templates"`. `fm = FastMail(config)`.
- `app/tasks/email_tasks.py` — concrete tasks.
- `app/templates/*.html` — Jinja2 templates.

## How to define a task

```python
# app/tasks/email_tasks.py
from pydantic import EmailStr
from fastapi_mail import MessageSchema
from app.core.mail import fm
from app.core.celery_app import celery


@celery.task(bind=True, max_retries=3)
def my_email(self, user_email: EmailStr, user_name: str):
    try:
        message = MessageSchema(
            subject="Subject",
            recipients=[user_email],
            template_body={"name": user_name},
            subtype="html",
        )
        asyncio.run(fm.send_message(message, template_name="my_template.html"))
    except Exception as e:
        raise self.retry(exc=e, countdown=60)
```

Rules:

- `bind=True` to get `self` and call `self.retry(...)`.
- `max_retries=3` by repo convention.
- `countdown=60` seconds between retries.
- `asyncio.run(...)` wraps FastMail's coroutine inside Celery (the worker is sync).
- `subtype="html"` always.
- Pass `template_body` with the variables the template uses.

## Templates

`app/templates/<name>.html`. Jinja2 with double braces: `{{name}}`, `{{surname}}`, `{{email}}`, `{{password}}`.

Repo pattern (see `welcome_mail.html`, `welcome_registration_mail.html`, `recover_password.html`):

- `<!doctype html>` + `<html>` + `<body>` with inline styles.
- Tracklinker logo: `https://i.ibb.co/8nYJMRgt/Large-Icon.png` (do not download or version it).
- Centered content, `max-width: 600px`, color `#333`, background `#f5f5f5`.
- Greeting: `Hola, <strong>{{name}} {{surname}}</strong>`.
- Language: **Spanish**, friendly tone.

## How to enqueue it

From a service:

```python
from app.tasks.email_tasks import my_email
...
my_email.delay(user_email=user.email, user_name=user.name)
```

`delay(...)` is non-blocking: it enqueues and returns. Do not use `.apply_async()` unless you need to schedule it for later.

## Usage patterns in the repo

| Trigger | Task | Template |
|---|---|---|
| `POST /api/users/create` (Admin creates a user of the parking) | `send_welcome_email` (with a temporary `password`) | `welcome_mail.html` |
| `PUT /api/auth/complete-on-boarding` (Admin onboarding) | `send_welcome_registration_email` | `welcome_registration_mail.html` |
| `POST /api/auth/recover-password` | `recovery_password_email` | `recover_password.html` |

## Required environment variables

In `.env` (see `.env.example`):

```
MAIL_USERNAME=<sender email>
MAIL_PASSWORD=<Gmail app password>
MAIL_FROM=<sender email>
```

The SMTP connection uses Gmail STARTTLS on port 587. For production, evaluate a transactional provider (SendGrid, Mailgun, SES) — **do not** change it without asking.

## Common errors

- `TEMPLATE_FOLDER` in `app/core/mail.py` is a **relative path** (`"app/templates"`). If you start uvicorn from another cwd, it fails. If it does, always start from the repo root.
- Forgetting `asyncio.run(...)` inside the task → the coroutine never runs.
- Passing a `dict` with keys the template does not use → literal `{{var}}` remains.
- Enqueuing before `connection.commit()` in the service → if the commit fails, the email still goes out. **Always enqueue after** the commit (see `auth_service.complete_onboarding` for the correct example).

## Anti-patterns

- Do not send emails synchronously inside an endpoint. Always via Celery.
- Do not read template files at runtime: they live on disk and Jinja2 caches them.
- Do not log email content (may contain passwords).
- Do not enqueue from a thread: `delay()` is called from the main process, the worker does the rest.
