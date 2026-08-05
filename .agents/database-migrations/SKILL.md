---
name: database-migrations
description: DDL/DML workflow for parking-hackathon-backend. Load when adding columns, tables, indexes, or seed data. Note: the project does NOT use Alembic — schema lives in `database/parking_db_ddl.sql`.
---

# Database migrations

## Files

The project tracks schema and seed data as plain SQL files in `database/`:

| File | Purpose |
|---|---|
| `database/parking_db_ddl.sql` | **Schema source of truth.** `CREATE TABLE`, `CREATE INDEX`, FK constraints. Run on a fresh dev DB. |
| `database/parking_db_dml.sql` | Dev seed: roles, countries, optional demo data. **Never** run in production. |
| `database/parking_db_view.sql` | The `CREATE VIEW` for `vw_parking_summary` plus a `SELECT * FROM vw_parking_summary` verification query. Run on a fresh dev DB. |

There is no `parking_db_*.sql` migration tool. The files are full re-creations (the DDL starts with `DROP DATABASE IF EXISTS parking_db; CREATE DATABASE …`). For dev, you re-run the DDL and DML from scratch.

## No migration tool

The project **does not** use Alembic, Flyway, or any other versioned migration tool. Schema changes are applied manually to the dev database (via MySQL Workbench, `mysql` CLI, or a `Docker exec`). When Alembic is introduced, this skill is replaced — until then, treat the SQL files as the contract.

Until Alembic lands, the workflow is:

1. Edit `database/parking_db_ddl.sql` so it matches the desired schema.
2. Apply the change manually on the dev database.
3. Commit the updated `.sql` file in the same PR as the code that depends on it.

If the change is non-trivial (drop column, rename, type change), capture the manual `ALTER` statement in the PR description so the reviewer can replay it.

## DDL workflow

When adding a column:

```sql
-- 1) Update the table definition in database/parking_db_ddl.sql
CREATE TABLE ENTRIES (
  id         INT NOT NULL AUTO_INCREMENT,
  parking_id INT NOT NULL,
  plate_id   INT NOT NULL,
  spot_id    INT NOT NULL,
  notes      TEXT NULL,                -- new column
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_entries_parking_id (parking_id),
  FOREIGN KEY (parking_id) REFERENCES PARKINGS(id),
  FOREIGN KEY (plate_id)   REFERENCES PLATES(id),
  FOREIGN KEY (spot_id)    REFERENCES SPOTS(spot_id)
);

-- 2) Apply manually on the dev DB
ALTER TABLE ENTRIES ADD COLUMN notes TEXT NULL AFTER spot_id;
```

You can sanity-check the new column from Python before shipping the code that reads it:

```python
# Sanity check after applying the ALTER
from app.core.database import get_connection

connection = get_connection()
try:
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'ENTRIES'"
    )
    print([row[0] for row in cursor.fetchall()])
finally:
    connection.close()
```

Rules:

- Update `parking_db_ddl.sql` so a fresh DB ends up with the same schema.
- Apply the `ALTER` to the running dev DB.
- For `DROP` / `RENAME`, do it in a two-step PR (add new column, deploy, backfill, remove old column) to avoid breaking live data.
- Keep `UPPER_SNAKE` table names. The repo uses this convention everywhere.
- Add an `INDEX` on every `parking_id` column. Multi-tenant reads filter by `parking_id` and a missing index is a production fire.

## DML workflow

The DML file is for **dev seed data only**:

- 3 `ROLES`: `Admin`, `Maquina`, `Cliente`.
- 195 `COUNTRIES` (UN member states + Vatican + Palestine).
- Other tables are empty; the test admin creates the parking through the API on first run.

**NEVER run `parking_db_dml.sql` in production.** It contains hardcoded credentials (a known repo issue — see `Anti-patterns` below). The production database should be created empty and populated through the public API.

If you need new seed data for tests, add it to `parking_db_dml.sql` behind a clear comment. Do not commit secrets there.

## Conventions

- **Table names**: `UPPER_SNAKE` (`PARKINGS`, `ENTRIES`, `PAYMENTS`).
- **Column names**: `snake_case` (`parking_id`, `created_at`, `vehicle_type_id`).
- **Foreign keys**: explicit `FOREIGN KEY (col) REFERENCES TABLE(col)` after the columns. **No `ON DELETE CASCADE`** — deletes are managed in the service layer.
- **Indexes**: every column used in `WHERE` for tenant filtering has an `INDEX idx_<table>_<col>`. Example: `INDEX idx_entries_parking_id (parking_id)`.
- **Timestamps**: `created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP`. `updated_at` is not used in the current schema.
- **Money / decimals**: prefer `INT` (cents) or `DECIMAL(10,2)` over `FLOAT`. The current schema uses `DECIMAL` in `RATES.value` and `PAYMENTS.value`.
- **Charset**: `utf8mb4` / `utf8mb4_unicode_ci` everywhere. The DDL sets it on the database, the docker-compose sets it on the server. Do not change it.
- **VARCHAR over TEXT for short fixed-set fields**: `TEXT`, `MEDIUMTEXT`, `LONGTEXT`, `BLOB` and `JSON` columns **cannot** have a `DEFAULT` value in MySQL (unless using MySQL 8.0.13+ expression default syntax `DEFAULT ('value')` with parens, which is not portable). For short fixed-set string fields like `USERS.provider` (which only ever holds `'Local'`, `'Google'`, or `'GitHub'`) use `VARCHAR(N) NOT NULL DEFAULT "value"` so the column can self-populate on ALTER. The set itself is enforced in the Python `Literal` + `frozenset(get_args(...))` pattern (see `code-conventions`).

## Worked example — `USERS.provider` and `USERS.google_id`

These two columns support the local-vs-Google distinction. They were added in the same PR as the Google login refactor:

```sql
-- database/parking_db_ddl.sql
CREATE TABLE USERS (
  ...
  provider VARCHAR(50) NOT NULL DEFAULT "Local",  -- not TEXT — needs DEFAULT
  google_id TEXT NULL,                            -- TEXT is fine, NULL is acceptable
  status INT NOT NULL DEFAULT 2,
  ...
  UNIQUE INDEX uq_users_google_id (google_id)
);
```

**Backfill recipe** (run on prod **before** the NOT NULL constraint takes effect, or before any INSERT that does not pass `provider`):

```sql
-- Idempotent. Safe to run multiple times.
UPDATE USERS
SET provider = 'Local'
WHERE provider IS NULL OR provider = '' OR provider = 'local' OR provider = 'google';
```

The `LOWER` clauses cover the case where someone hand-seeded with lowercase. After this, all existing rows have a valid `provider` and the constraint is safe to enforce.

**Why the unique index on `google_id`**: the same Google account could otherwise create two users in our DB if the user logs in twice with different emails but the same Google `sub` (which is the stable identity). The unique index prevents that. `google_id` is NULL-able because Local users don't have one.

## Anti-patterns

- **Committing credentials to `parking_db_dml.sql`.** The current file has hardcoded test credentials (a known issue). When cleaning it up, move the demo data to a `.example` file or behind a `dev_seed.py` script that reads from `.env`. **Do not add new credentials.**
- **Using the DML file in production.** It is a dev-only seed. Production data comes from the API.
- **Applying DDL changes without updating the DDL file.** The DDL is the source of truth. A manual `ALTER` that is not reflected in the DDL is a drift bomb.
- **Adding `ON DELETE CASCADE`.** The repo manages cascading deletes by hand in the service layer (`delete_floor` → `delete_spots_by_floor` → `delete_floor`). Adding DB-level cascades can hide business rules.
- **Creating a new migration tool without coordinating.** When Alembic lands, the workflow changes globally. Do not introduce it ad-hoc.
- **Renaming a column without checking every `SELECT`.** The repos use raw SQL — there is no model registry to catch renames. Grep the repo for the old column name first.

## Common errors

- `Unknown column 'x' in 'field list'` → a code change used a column that the DB does not have. Re-run the DDL or apply the missing `ALTER`.
- `FOREIGN KEY constraint fails` on `INSERT` → the FK target is missing or has a different type (most common: `INT` vs `BIGINT`). Check the DDL.
- Duplicate seed IDs on a re-run → the DML file uses `INSERT` without `ON DUPLICATE KEY UPDATE` or `INSERT IGNORE`. For a fresh dev DB this is fine; for re-runs, wrap inserts with `INSERT IGNORE` or reset the DB first.

## Required environment variables

This skill does not introduce new env vars, but applying the DDL requires:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (see `config-and-settings`).
