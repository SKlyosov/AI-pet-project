---
phase: "1"
slug: "fundament-vybor-steka-i-skelet-proekta"
status: draft
nyquist_compliant: true
wave_0_complete: false
created: "2026-11-18"
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.2.0 + pytest-django 4.14.0 (устанавливаются в Wave 0 — скелета ещё нет) |
| **Config file** | `pyproject.toml` — секция `[tool.pytest]` c `DJANGO_SETTINGS_MODULE = "config.settings.test"` (native TOML, pytest 9+) — создаёт план 01-01 |
| **Quick run command** | `docker compose run --rm web pytest -x -q` (host-Python отсутствует — docker-first, Pitfall 8) |
| **Full suite command** | `docker compose run --rm web pytest -v` (coverage — в CI) |
| **Estimated runtime** | ~30 секунд (скелет: healthz + smoke) |

---

## Sampling Rate

- **After every task commit:** Run `docker compose run --rm web pytest -x -q` (host-Python отсутствует — docker-first, Pitfall 8)
- **After every plan wave:** Run `docker compose config --quiet` + `docker compose run --rm web pytest -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-T1 | 01-01 | 1 | SC-1 | — | — | artifact | `findstr /C:Consequences docs\adr\0001-choice-of-stack.md` | ❌ Wave 0 | ⬜ |
| 01-01-T2 | 01-01 | 1 | SC-1 | T-01-01, T-01-02 | секреты только в .env*; пины == | artifact | `findstr /C:Django==5.2.19 requirements\base.txt && findstr /C:[tool.pytest] pyproject.toml && findstr /C:eol=lf .gitattributes` | ❌ Wave 0 | ⬜ |
| 01-02-T1 | 01-02 | 2 | SC-2, SC-4 | T-01-03, T-01-04 | healthz без внутренностей; порты db/cache 127.0.0.1 | integration (docker) | `docker compose down -v && docker compose up -d --build --wait && curl -fsS http://localhost:8000/healthz && curl -fsS http://localhost:8000/ | findstr /C:hit-counter && docker compose run --rm web python manage.py migrate --check && docker compose run --rm web pytest -x -q` | ❌ Wave 0 | ⬜ |
| 01-02-T2 | 01-02 | 2 | SC-2, SC-4 | T-01-03 | — | smoke (docker) | `scripts\verify_bootstrap.cmd` (маркер BOOTSTRAP_OK) | ❌ Wave 0 | ⬜ |
| 01-03-T1 | 01-03 | 3 | SC-2 (D-04) | — | — | artifact + integration | `findstr /C:apps.accounts config\settings\base.py && docker compose run --rm web python manage.py makemigrations --check --dry-run` | ❌ Wave 0 | ⬜ |
| 01-03-T2 | 01-03 | 3 | SC-2 | T-01-05, T-01-06 | DEBUG=False; ALLOWED_HOSTS из env | artifact + integration | `findstr /C:ALLOWED_HOSTS config\settings\prod.py && docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py check` | ❌ Wave 0 | ⬜ |
| 01-03-T3 | 01-03 | 3 | SC-2 (docs) | — | — | artifact | `findstr /C:verify_bootstrap README.md && findstr /C:pytest AGENTS.md && findstr /C:ruff AGENTS.md` | ❌ Wave 0 | ⬜ |
| 01-04-T1 | 01-04 | 4 | SC-3 | T-01-07 | permissions: contents: read | artifact | `findstr /C:setup-python .github\workflows\ci.yml && findstr /C:postgres:18 .github\workflows\ci.yml && findstr /C:ruff .github\workflows\ci.yml` | ❌ Wave 0 | ⬜ |
| 01-04-T2 | 01-04 | 4 | SC-3, SC-4 | T-01-SC | пины == в CI | integration | `docker compose run --rm web ruff check . && docker compose run --rm web mypy . && docker compose run --rm web python manage.py makemigrations --check --dry-run && docker compose run --rm web pytest -v` | ❌ Wave 0 | ⬜ |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

> Заполняется планами: pytest/pytest-django/coverage — уже в requirements/dev.txt (план 01-01); `tests/conftest.py`, `tests/test_health.py`, `config/settings/test.py`, pyproject `[tool.pytest]` — план 01-02 Task 1 (tracer); `.github/workflows/ci.yml` — план 01-04; скрипт приёмки — план 01-02 Task 2.

- [x] Dev-зависимости определены (pytest, pytest-django, ruff, mypy+django-stubs, coverage) — requirements/dev.txt, план 01-01
- [x] `tests/conftest.py` и первый тест-набор (healthz smoke + счётчик) спланированы — план 01-02 Task 1 (создаются при исполнении Wave 2)
- [x] compose config validation включена в per-wave sampling

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `docker compose up` поднимается одной командой с нуля (SC-2) | SC-2 | Требует чистого окружения/томов | `docker compose down -v` → `docker compose up --build` → `curl localhost:8000/healthz` отвечает 200 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
