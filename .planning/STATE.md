---
gsd_state_version: "1.0"
current_phase: 1
current_phase_name: Фундамент — выбор стека и скелет проекта
status: verifying
stopped_at: Completed 01-04-PLAN.md
last_updated: "2026-11-18T10:06:46.646Z"
last_activity: 2026-11-18
last_activity_desc: Phase 1 execution started
state_head: bf5b7e24474f5725657980b6f2dd882b452af7df
progress:
  total_phases: 10
  completed_phases: 0
  total_plans: 4
  completed_plans: 4
  percent: 0
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-11-18)

**Core value:** Объявление частного лица находят покупателя — оно не тонет среди коммерческих предложений.
**Current focus:** Phase 1 — Фундамент — выбор стека и скелет проекта

## Current Position

Phase: 1 (Фундамент — выбор стека и скелет проекта) — EXECUTING
Plan: 4 of 4
Status: Phase complete — ready for verification
Last activity: 2026-11-18 — Phase 1 execution started

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 01 P01 | 6min | 2 tasks | 8 files |
| Phase 01 P02 | 26min | 2 tasks | 23 files |
| Phase 01 P03 | 24min | 3 tasks | 23 files |
| Phase 01 P04 | 6min | 2 tasks | 2 files |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Roadmap: порядок фаз следует research/SUMMARY.md (зависимости данных); фотографии перенесены до публичных страниц, чтобы страницы и поиск рендерили фото без ретрофита
- Roadmap: правило инвариантов — квота ≤10, hard delete и политика `ON DELETE SET NULL` + снапшот-поля закладываются в Phase 4 (владелец таблицы listings)
- Roadmap: Phase 1 — user gate выбора стека (ADR) до какого-либо scaffold (правило AGENTS.md)
- Roadmap: фазы 7 (поиск) и 8 (мессенджер) зависят от фазы 6 и могут исполняться параллельно (parallelization включён)
- [Phase 01]: 01-01: ADR-0001 fixes Variant B (Django 5.2 LTS + DRF, PostgreSQL 18, Redis 8) as the user's explicit choice; all 14 deps pinned ==, mypy held at 1.19.1 (django-stubs 5.2.9 range)
- [Phase 01]: 01-02: entrypoint.sh dual-purpose: migrate -> collectstatic -> exec gunicorn for normal start, exec "$@" when args passed — ENTRYPOINT-form entrypoint.sh ignores run-command args; the plan-prescribed `docker compose run --rm web pytest / migrate --check` would boot gunicorn instead of the command. The exec "$@" branch keeps the verbatim start sequence and makes one-off commands reachable through the single entrypoint.
- [Phase 01]: 01-02: /healthz registered both with and without trailing slash — Probe targets (curl in the verify chain, compose healthcheck urllib) request /healthz without a slash; with only healthz/ registered Django APPEND_SLASH answers 301 with an empty body, which fails the "curl prints ok" gate. The alias serves 200 JSON directly; the key_link pattern path("healthz/", healthz) is preserved.
- [Phase 01]: 01-02: compose host ports 127.0.0.1:15432/16379 and pgdata mounted at /var/lib/postgresql — Host-local PostgreSQL (PID 19092) and Redis (PID 35872) already bind 5432/6379 on this machine; user services were not touched, loopback-only posture (T-01-04) kept, in-network addressing (db:5432, cache:6379) unchanged. postgres:18+ images reject a direct /var/lib/postgresql/data mount and require the versioned layout at /var/lib/postgresql (docker-library/postgres PR #1259).
- [Phase 01]: 01-02: config/settings/base.py carries explicit DEBUG=False and ALLOWED_HOSTS=[] safe defaults — The plan pinned DEBUG/ALLOWED_HOSTS only for dev; explicit safe defaults in base follow the Django deployment checklist and ASVS V14 so a missing override can never silently enable debug.
- [Phase 01]: D-04 materialized: 7 domain apps are empty AppConfig scaffolds (no models.py/migrations) — module boundaries are fixed while cheap, before any domain tables exist — Pattern 3 research: boundaries get more expensive with every foreign table; Pattern 4: first migration needs no fake schema — accounts gets custom User in Phase 2 before user data exists (ADR-0001)
- [Phase 01]: docker compose run executes image-baked code, not the working tree — rebuild (docker compose build web) after code changes before re-running compose-run gates — Found when prod.py check hit ModuleNotFoundError on a freshly written module: the 01-02 image predated it; all Task gates were re-run green on the rebuilt image and the rule is documented in README/AGENTS.md
- [Phase 01]: SECURE_BROWSER_XSS_FILTER from the plan is not set: the setting was removed in Django 4.0 and is absent from Django 5.2 (verified against django.conf.global_settings); XSS mitigation for template phases is Content-Security-Policy — Setting an inert flag would fake a security control, violating the repo's verified-facts rule; removal fact and the CSP path are documented in config/settings/prod.py comments
- [Phase 01]: 01-04: CI workflow — один job с четырьмя поимёнными steps (ruff → mypy → makemigrations --check --dry-run → pytest) на services postgres:18+redis:8, least-privilege contents:read; DJANGO_SETTINGS_MODULE=config.settings.test закреплён в job env, чтобы manage.py-ступень drift-check шла через те же test-настройки, что pytest читает из pyproject; зелёность на GitHub фиксируется первым пушем ветки (/gsd-verify-work)
- [Phase 01]: 01-04: локальное зеркало CI зелёное без правок pyproject.toml — все четыре ступени (ruff/mypy/drift-check/pytest, 2 passed) exit 0 в docker compose run на конфигах 01-01; workflow не ссылается на неработающие команды

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: выбор стека A/B/C открыт — блокирует все фазы до ADR (осознанный user gate, не дефект)

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-11-18T10:06:46.565Z
Stopped at: Completed 01-04-PLAN.md
Resume file: None
