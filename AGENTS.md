# AGENTS.md

Greenfield product repo: private classifieds web service (RU-language). Planning artifacts live in `.planning/` (GSD: PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md, config.json, research/). Source is a Django 5.2 modular-monolith skeleton (`config/` project, `apps/` modules) run via docker compose (PostgreSQL 18 + Redis 8, gunicorn + WhiteNoise); OpenCode agent config lives in `.opencode/`. Docs: `README.md` (RU quickstart), `docs/PRD.md`, `docs/adr/0001-choice-of-stack.md`. CI: `.github/workflows/ci.yml` (GitHub Actions — one job per push/PR: ruff → mypy → `makemigrations --check --dry-run` → pytest, with postgres:18 + redis:8 services; first run happens on the first push of a branch).

## Ground rules

- **Stack is fixed by ADR-0001: Django 5.2 LTS + DRF, PostgreSQL 18, Redis 8, Python 3.13.** Modular monolith: 8 apps in `apps/` (`core` + 7 domain). Module boundary = table ownership: cross-app data access only via the owner's service function, never via another app's ORM models.
- **No direct commits to `main`.** Work happens on `feat/<name>`, `fix/<name>`, or `chore/<name>` branches; commit messages follow Conventional Commits. Enforced by `.opencode/rules/git-main-protection.md`.
- **Docker-first workflow — the host has no `python`/`pip` in PATH** (only the `py` 3.14 launcher, outside the tested classifiers of gunicorn 27 / django-stubs 5.2.9). Every command runs through docker compose:
  - start the stack: `docker compose up -d --build --wait` (liveness: `curl http://localhost:8000/healthz`)
  - tests: `docker compose run --rm web pytest -x -q`
  - lint: `docker compose run --rm web ruff check .`
  - types: `docker compose run --rm web mypy .`
  - skeleton acceptance, resets the dev DB: `scripts\verify_bootstrap.cmd` (Windows) / `scripts/verify_bootstrap.sh` (Unix)
  - the container runs the code baked into the image — rebuild (`docker compose build web`) after changing code, then re-run `docker compose run`

## Planning workflow (GSD)

- `.planning/ROADMAP.md` holds 10 phases; `.planning/STATE.md` tracks the current position.
- Phase lifecycle: `/gsd-discuss-phase <N>` (optional) → `/gsd-plan-phase <N>` → `/gsd-execute-phase <N>`; `/gsd-progress` shows status.
- Planning docs are committed to git (`commit_docs: true`); config in `.planning/config.json` (yolo, fine granularity, parallel execution, inherit models).

## Keeping this file useful

- Update this file the same commit that adds tooling, structure, or conventions. Verified facts only; omit anything you can't check.
