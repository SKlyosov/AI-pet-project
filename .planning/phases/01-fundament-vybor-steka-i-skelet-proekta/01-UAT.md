---
status: testing
phase: 01-Фундамент — выбор стека и скелет проекта
source: [01-VERIFICATION.md]
started: 2026-04-01T12:10:00Z
updated: 2026-04-01T12:10:00Z
---

## Current Test

number: 1
name: Уронить зависимость и проверить /healthz → 503
expected: |
  503 {"status": "fail"} без раскрытия внутренностей; после подъёма зависимости — 200 ok
awaiting: user response

## Tests

### 1. Уронить зависимость и проверить /healthz → 503
expected: 503 {"status": "fail"} без раскрытия внутренностей (без версий/хостов/DSN); после подъёма зависимости — снова 200 {"status": "ok", "checks": {...}}
result: [pending]

### 2. Первый прогон CI на GitHub
expected: Запушить ветку chore/skeleton в origin; job check зелёный поимённо: Lint (ruff) → Typecheck (mypy) → Migrations drift check → Tests; actions/checkout@v7 и actions/setup-python@v7 резолвятся
result: [pending]

### 3. Решить расхождение Mode: mvp vs формат цели фазы
expected: Либо переформулировать цель фазы (/gsd-mvp-phase 1 — «As a…, I want…, so that…»), либо осознанно принять стандартную goal-backward верификацию (уже выполнена, 21/22) и/или снять Mode: mvp с инфраструктурных фаз ROADMAP
result: [pending]

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps
