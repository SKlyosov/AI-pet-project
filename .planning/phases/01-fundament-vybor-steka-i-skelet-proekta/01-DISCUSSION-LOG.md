# Phase 1: Фундамент — выбор стека и скелет проекта - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-18
**Phase:** 1-Фундамент — выбор стека и скелет проекта
**Areas discussed:** выбор стека (user gate), структура репозитория, инфраструктура/tooling, миграции, runtime
**Mode:** `--auto` (авто-выбор рекомендованных опций; стек — единственный явный вопрос пользователю)

---

## Выбор стека (A/B/C)

| Option | Description | Selected |
|--------|-------------|----------|
| A: TypeScript | NestJS 12 + Next.js 16 + PostgreSQL 18 + Prisma 7 + Redis 8 — рекомендация research (SSR/SEO, один язык) | |
| B: Python / Django | Django 5.2 LTS + DRF — Django Admin бесплатно закрывает оба админ-справочника PRD | ✓ |
| C: Kotlin / Spring | Spring Boot 4.1 + JDK 25 — JVM-надёжность, преимущество для домена не реализуется | |

**User's choice:** B: Python / Django
**Notes:** Явный user gate по правилу AGENTS.md и критерию приёмки фазы 1 («выбор сделал пользователь, а не агент»). Рекомендацией research был вариант A; пользователь предпочёл Django Admin для админ-справочников.

---

## Структура репозитория

| Option | Description | Selected |
|--------|-------------|----------|
| Единая монорепа монолита | Один Django-проект с приложениями-модулями по границам домена | ✓ |
| Раздельные репозитории API/web | Два сервиса с первого дня | |

**User's choice:** [auto] Единая монорепа монолита (recommended default — модульный монолит из ARCHITECTURE.md)

## CI

| Option | Description | Selected |
|--------|-------------|----------|
| GitHub Actions | lint (ruff) + typecheck (mypy) + tests (pytest) на каждый пуш/PR | ✓ |
| Без CI на старте | Только локальные проверки | |

**User's choice:** [auto] GitHub Actions (recommended default)

## docker-compose

| Option | Description | Selected |
|--------|-------------|----------|
| PG 18 + Redis 8 + app + health-check | Минимальный контур фазы 1; S3/MinIO — в Phase 5 | ✓ |
| Включить MinIO сразу | Объектное хранилище заранее | |

**User's choice:** [auto] PG 18 + Redis 8 + app + health-check (recommended default)

## Миграции

| Option | Description | Selected |
|--------|-------------|----------|
| Нативные Django migrations | Встроенный механизм выбранного стека | ✓ |
| Внешний инструмент (Flyway/alembic standalone) | Требует отдельной настройки | |

**User's choice:** [auto] Нативные Django migrations (recommended default; следует из выбора B)

## Runtime

| Option | Description | Selected |
|--------|-------------|----------|
| Python 3.12+, gunicorn WSGI | Достаточно для v1; ASGI — при realtime (v2+) | ✓ |
| ASGI/uvicorn сразу | Под будущий WebSocket | |

**User's choice:** [auto] Python 3.12+ + gunicorn WSGI (recommended default; скорректировано под выбор B — изначальный вариант node:26 относился к варианту A)

---

## Agent's Discretion

- Версии второстепенных зависимостей, структура settings, конфигурация линтеров, способ раздачи статики.

## Deferred Ideas

None — discussion stayed within phase scope.
