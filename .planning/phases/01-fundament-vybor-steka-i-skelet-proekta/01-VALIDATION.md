---
phase: "1"
slug: "fundament-vybor-steka-i-skelet-proekta"
status: draft
nyquist_compliant: false
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
| **Config file** | `pyproject.toml` / `pytest.ini` — создаётся в Wave 0 |
| **Quick run command** | `python -m pytest -x -q` |
| **Full suite command** | `python -m pytest --cov` |
| **Estimated runtime** | ~30 секунд (скелет: healthz + smoke) |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest -x -q`
- **After every plan wave:** Run `docker compose config --quiet` + `python -m pytest --cov`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (заполняется планировщиком при создании PLAN.md) | | | | | | | | | |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] Установка dev-зависимостей (pytest, pytest-django, ruff, mypy+django-stubs, coverage)
- [ ] `tests/conftest.py` — базовые fixtures (django_db, settings)
- [ ] Первый тест-стаб: healthz smoke + compose config validation

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
