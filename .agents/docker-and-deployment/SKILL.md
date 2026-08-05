---
name: docker-and-deployment
description: Docker setup for parking-hackathon-backend. Load when touching the DockerFile, docker-compose, or deploying locally with containers.
---

# Docker & deployment

## Files

- `DockerFile` — single-stage image based on `python:3.13-slim` with `uv` for dependency management. Runs the API as `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- `docker-compose.dev.yml` — local stack: MySQL 8.0 + Redis 7 + Qdrant + API + Celery worker, all on a private bridge network.
- `.env` and `.env.docker` — env files. The compose stack reads **both** (`env_file: [.env, .env.docker]`, with `.env.docker` overriding).

The `DockerFile` is **dev-oriented as-is**: no multi-stage build, no non-root user, no production hardening. Use it for local stacks and CI. For production, derive a hardened image (multi-stage, distroless, non-root) on top of this one.

## Services (`docker-compose.dev.yml`)

| Service | Image | Ports | Volumes | Healthcheck | Env |
|---|---|---|---|---|---|
| `db` | `mysql:8.0` | `3306:3306` | `mysql_data_dev:/var/lib/mysql` | `mysqladmin ping` every 10s | `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE` from `.env` |
| `redis` | `redis:7-alpine` | `6379:6379` | `redis_data_dev:/data` | none | — |
| `qdrant` | `qdrant/qdrant:latest` | `6333:6333`, `6334:6334` | `qdrant_data_dev:/qdrant/storage` | none | `QDRANT__SERVICE__GRPC_PORT=6334` |
| `api` | local build (`DockerFile`) | `8000:8000` | — | none (depends on `db` healthy, `redis` started, `qdrant` started) | `.env` + `.env.docker` |
| `celery_worker` | local build (`DockerFile`) | — | — | none (depends on `db` healthy, `redis` started; `qdrant` is not required because the worker does not touch RAG) | `.env` + `.env.docker` |

All services share the `parking-net` bridge network. Service names (`db`, `redis`, `qdrant`, `api`, `celery_worker`) are the DNS hostnames the containers see each other as.

## Local run

From the repo root:

```bash
docker compose -f docker-compose.dev.yml up --build
```

The first build installs the dependencies with `uv sync --frozen --no-dev` (see the `DockerFile`). The `api` and `celery_worker` wait for `db` to pass its healthcheck before starting.

A quick Python check that the stack is up and the chatbot can reach Qdrant:

```python
# Once the stack is running
from app.core.config import settings
from app.core.qdrant import init_qdrant

qdrant = init_qdrant()
collections = {c.name for c in qdrant.get_collections().collections}
assert "parking_knowledge" in collections
print(f"Qdrant OK on {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
```



To stop and wipe data:

```bash
docker compose -f docker-compose.dev.yml down            # stop, keep volumes
docker compose -f docker-compose.dev.yml down -v         # stop, drop volumes
```

The Qdrant container keeps its data in `qdrant_data_dev` — drop the volume if you change the embedding model and the existing collection has a different size.

## Celery worker

Same `DockerFile` as the API, different command:

```yaml
celery_worker:
  build:
    context: .
    dockerfile: DockerFile
  command: celery -A app.core.celery_app.celery worker --loglevel=info
```

It must see `REDIS_URL` to enqueue and dequeue tasks. The `.env` file is enough.

## Volumes

| Volume | Mounted on | Survives `down`? |
|---|---|---|
| `mysql_data_dev` | `/var/lib/mysql` (db) | yes |
| `redis_data_dev` | `/data` (redis) | yes |
| `qdrant_data_dev` | `/qdrant/storage` (qdrant) | yes |

If you change the schema (DDL) or the embedding model, drop the relevant volume and re-create the container.

## Env files

The compose file reads two env files in order: `.env` (host-side values) and `.env.docker` (hostnames for inside the network). The typical pattern:

- `.env`: `DB_HOST=localhost`, `REDIS_URL=redis://localhost:6379/0`, `QDRANT_HOST=localhost`.
- `.env.docker`: `DB_HOST=db`, `REDIS_URL=redis://redis:6379/0`, `QDRANT_HOST=qdrant`.

So the same `.env` is reusable for "run uvicorn on the host" and "run the whole stack in docker" without editing the values.

## Anti-patterns

- **Running without `.env`.** The API will fail to start (see `config-and-settings`).
- **Hardcoding credentials in compose.** Use env references (`${DB_PASSWORD}`). The current compose file already does this — keep it that way.
- **Building a production image from this `DockerFile` as-is.** There is no non-root user, no healthcheck, no multi-stage. Use it for dev, derive a hardened image for prod.
- **Re-using the `parking-net` network for an unrelated stack.** It is a project-scoped bridge. If you need to talk to another compose stack, expose ports or use an external network.
- **Forgetting to mount `qdrant_data_dev` as a volume.** Qdrant will lose all chunks on every container restart, and the chatbot will return empty RAG results.
- **Using `:latest` for `qdrant/qdrant`.** Pin the image tag if you need reproducible builds. The compose currently uses `:latest` because the project is moving fast on this dep — change it when the API stabilizes.
- **Skipping the `db` healthcheck.** Without it, the API and Celery worker may start before MySQL is ready and crash on the first connection.

## Common errors

- `connection refused` to MySQL on first boot → wait for the `db` healthcheck to pass; the `api` has `depends_on: condition: service_healthy`.
- Celery tasks not consumed → the worker container has the same image but a different `command`. Check `docker compose ps` and `docker compose logs celery_worker`.
- Chatbot returns empty RAG → Qdrant is reachable but the collection is empty. Run `rebuild_parking_knowledge(parking_id)` for one parking (the easiest way is to call `tool_update_parking` from the chatbot or to re-trigger onboarding).
- `uv sync` fails in the build → `uv.lock` and `pyproject.toml` are out of sync. Re-run `uv lock` locally and commit.

## Required environment variables

The compose file reads them from `.env` + `.env.docker`. See `config-and-settings` for the full list. The minimum for the stack to boot:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `REDIS_URL`
- `ACCESS_TOKEN_SECRET_KEY`, `REFRESH_TOKEN_SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE`, `REFRESH_TOKEN_EXPIRE`
- `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`
- `AI_API_KEY`, `AI_BASE_URL`, `AI_MODEL` (if `CHATBOT_ENABLED=True`)
- `QDRANT_HOST`, `QDRANT_PORT`, `EMBEDDING_MODEL` (if `CHATBOT_ENABLED=True`)
- `HF_TOKEN` (only if the embedding model is gated)
- `ENVIRONMENT`
