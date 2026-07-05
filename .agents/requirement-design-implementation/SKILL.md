---
name: requirement-design-implementation
description: Mandatory 3-phase flow every task must follow in parking-hackathon-backend: Requirements → Design → Implementation. Load before starting any task.
---

# Requirement → Design → Implementation

**Non-negotiable rule** (see `AGENTS.md §8`): no phase is skipped. Each phase must produce an explicit deliverable before moving to the next.

When the user asks for something, open this skill **first** and work phase by phase.

---

## Phase 1 — Requirements

**Goal:** understand what needs to be done, without touching code.

Steps:

1. Reformulate the request in one or two sentences. If you can't, ask before continuing.
2. List:
   - **Affected actors** (`Admin`, `Cliente`, anonymous).
   - **Likely endpoint(s)** or changes to existing ones (path + verb).
   - **Input data** (schemas) and **output data** (responses).
   - **Explicit business rules**: validations, multi-tenant, roles.
   - **Error cases** the user will see (in Spanish, friendly).
3. List **open questions** if any. If there are any, **stop** and ask the user before continuing.
4. Load the skills you will touch (at least `code-conventions`, `api-layer` and/or `database-and-repository`).

**Output of the phase:**

> **Requirements**:
> - [list of points 1–3]
>
> **Skills to use**: `code-conventions`, `api-layer`, …
>
> **Open questions**: [if any] / none.

Wait for confirmation or answers to the questions before moving to phase 2.

---

## Phase 2 — Design

**Goal:** define **how** to do it, in which files, without writing the full code.

Steps:

1. Decide whether it is a **new feature** or a **modification**:
   - New → load `feature-scaffold`.
   - Modification → enumerate the files to touch.
2. Define the flow by layers:
   - `route` → middlewares, `RateLimiter`, schema, controller call.
   - `controller` → map service tuple to HTTPException / JSON.
   - `service` → order of repository calls, `commit/rollback`, business validations.
   - `repository` → SQL query (in your head first, then transcribed), cursor, response mapping.
3. For new queries, write the SQL by hand in the design and verify it uses parameterized `%s`, filters by `parking_id` and maps the response to a pydantic model.
4. If it touches Celery / email, decide the task and the template (see `email-and-tasks`).
5. If it touches auth (role, onboarding, password), decide the middleware to apply (see `auth-and-security`).
6. Verify that each repository result is a **pure function** over `connection`: it does not open or close the connection.
7. Anticipate tests / manual smoke checks (curl, `/docs`).

**Output of the phase:**

> **Design**:
> - **Route(s)**: `POST /api/<x>/create` …
> - **Files to create / touch**:
>   - `app/features/<x>/routes/<x>_routes.py` — add …
>   - `app/features/<x>/controllers/<x>_controller.py` — …
>   - …
> - **SQL**:
>   ```sql
>   SELECT … FROM PLATES WHERE parking_id = %s AND id = %s
>   ```
> - **Flow**: rate limit 30/min, Admin role, validation with `safe_str`, transaction with commit at the end.
> - **Risks / doubts**: …

Wait for the green light before moving to phase 3.

---

## Phase 3 — Implementation

**Goal:** execute the design, adjusting only what the real code forces you to change.

Steps:

1. Create / edit files in the order: `models/schemas` → `models/responses` → `repository` → `service` → `controller` → `route` → `main.py` (router include) for a new feature.
2. Comply with **all** rules in `code-conventions`: tuples, `ServiceError`, logger, `safe_str`, `finally: connection.close()`, Spanish messages.
3. If a step forces you to deviate from the design, **mention it explicitly** at the end.
4. **Do not** add dependencies to `pyproject.toml` without asking.
5. **Do not** touch the existing response shape without coordinating with the frontend.
6. After finishing, mentally run the happy path and at least one error case for each new endpoint.

**Output of the phase:**

> **Implementation**:
> - Changes: `app/features/<x>/...` (+N lines), `app/main.py` (+1 include_router).
> - **Deviations from the design**: none / [list with justification].
> - **Pending**: [if any] / none.
> - **Suggested commit**: `feat(<x>): <description>`.

---

## Flow summary

```
User request
   │
   ▼
1. Requirements (what)         ← deliver and wait for OK
   │
   ▼
2. Design (how, in which file) ← deliver and wait for OK
   │
   ▼
3. Implementation (code)       ← deliver and show the suggested commit
```

**Never** mix the phases. If at any phase you realize you need info from the user, **ask** with the `question` tool before inventing.
