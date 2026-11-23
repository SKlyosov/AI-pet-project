---
status: testing
phase: 01-Фундамент — выбор стека и скелет проекта
source: [01-VERIFICATION.md]
started: 2026-04-01T12:10:00Z
updated: 2026-04-01T12:10:00Z
---

## Current Test

number: 3
name: Решить расхождение Mode: mvp vs формат цели фазы
expected: |
  Закрывается решением по перестройке ROADMAP: Mode: mvp снимается с инфраструктурно-дизайнерских фаз 1–3
awaiting: user confirmation at phase close

## Tests

### 1. Уронить зависимость и проверить /healthz → 503
expected: 503 {"status": "fail"} без раскрытия внутренностей (без версий/хостов/DSN); после подъёма зависимости — снова 200 {"status": "ok", "checks": {...}}
result: pass (2026-04-01T14:05:00Z, agent) — `docker compose stop db` → curl → `{"status": "fail", "checks": {}}` (503-ветка, внутренности не раскрыты) → `docker compose up -d --wait` → curl → `{"status": "ok", "checks": {"db": "ok", "cache": "ok"}}`

### 2. Первый прогон CI на GitHub
expected: Запушить ветку (home-work-2, переименована из chore/skeleton) в origin; job check зелёный поимённо: Lint (ruff) → Typecheck (mypy) → Migrations drift check → Tests; actions/checkout@v7 и actions/setup-python@v7 резолвятся
result: in_progress — прогон #1 (94cde32, push пользователя) упал на ступени Lint: ruff EXE001 (manage.py имеет shebang, но закоммичен неисполняемым; в docker-образе маскировалось chmod-шагом Dockerfile). Диагностировано точным воспроизведением CI-дерева в контейнере; фикс — коммит 819fb16 (git update-index --chmod=+x manage.py) на ветке gsd/phase-2-ux-dizayn-vsego-produkta. Ожидает зелёного прогона после пуша ветки с фиксом.

### 3. Решить расхождение Mode: mvp vs формат цели фазы
expected: Либо переформулировать цель фазы (/gsd-mvp-phase 1 — «As a…, I want…, so that…»), либо осознанно принять стандартную goal-backward верификацию (уже выполнена, 21/22) и/или снять Mode: mvp с инфраструктурных фаз ROADMAP
result: resolved (decision) — принято решение о перестройке ROADMAP на горизонтальные слои (UX → UI → бэкенд): Mode: mvp снимается с фаз 1–3 (инфраструктура/дизайн, не User-Story форма), сохраняется на бэкенд-фазах; для фазы 1 принимается выполненная goal-backward верификация. Формально закрывается при /gsd-verify-work 1.

## Summary

total: 3
passed: 1
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
