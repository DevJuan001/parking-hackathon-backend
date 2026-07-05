---
name: commits-and-prs
description: Conventional commits, branching and PR conventions for parking-hackathon-backend. Load before `git commit` or `gh pr create`.
---

# Commits & PRs

## Conventional Commits — format

```
<type>: <short description in lowercase>
```

Allowed types (aligned with the `git log` history):

| Type | When |
|---|---|
| `feat` | New user-facing functionality (endpoint, schema, task). |
| `fix` | Bug fix. |
| `refactor` | Internal change without altering behavior. |
| `chore` | Maintenance, configs, deps, .gitignore. |
| `docs` | Documentation only (includes this `AGENTS.md` and the skills). |
| `test` | Add or fix tests. |

Rules:

- Lowercase message, no trailing period.
- One intent per commit. If you're mixing things, split the commit.
- If it touches a feature: `feat(parking): add bulk plate import endpoint` (scope optional but recommended).
- Issue references: `feat: add plate validation #42`.
- **Do not** commit `.env`, secrets, DB dumps, or `uv.lock` without justified reason.
- **Do not** commit `__pycache__/`, `.venv/`.

## Before committing — checklist

```bash
git status
git diff --stat
git log --oneline -5
```

- Stage only the intended files.
- Read the full diff: no stray `print(...)`, test `TODO`s, `console.log`, secrets.
- If you modified `pyproject.toml` or `uv.lock`, make sure it is necessary (otherwise revert).

## Commit message

Good:

```
feat(spots): add bulk delete endpoint
fix(payments): avoid charging when entry_time > now
refactor(spots): split update_spot into two queries
chore: bump fastapi to 0.136.3
docs: update requirement-design-implementation skill
```

Bad:

```
Cambios
fix bug
WIP
feat: add stuff to the app and also fix the bug i found
```

## Branching

- Main branch: `main`. Protected.
- For a task: a branch with a descriptive prefix:
  - `feat/<short>` — new features.
  - `fix/<short>` — bugfixes.
  - `refactor/<short>` — refactors.
  - `chore/<short>` — maintenance.
- Examples: `feat/exit-cancel`, `fix/payments-total-decimal`, `refactor/extract-floors-repository`.

```bash
git checkout -b feat/exit-cancel
```

## Push and PR

```bash
git push -u origin feat/exit-cancel
gh pr create --base main --title "feat: add exit cancel" --body "..."
```

- PR title = type + short description (same format as the main commit).
- PR body: 1) what changes, 2) why, 3) how to test it, 4) screenshots if there's UI.
- If the PR is >300 lines, split it.
- Before requesting review: `git status` clean, CI green, description filled.
- If you find a divergence between code and `AGENTS.md` / skills, **mention it in the PR** and update the skill in the same PR (or in a separate `docs:` one).

## Merge

- Squash or merge commit depending on team preference; the current repo log (`git log --oneline`) shows atomic commits without squash, so respect that style by default.
- Delete the remote branch after the merge.

## Versioning and tags

The project does not use automated `bumpversion` or `semver` (version lives in `pyproject.toml:3` and `app/main.py:36`). If a change is release-worthy, update those two by hand and tag it:

```bash
git tag -a v0.2.0 -m "feat: ..."
```
