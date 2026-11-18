# Phase 1: Фундамент — выбор стека и скелет проекта - Context

**Gathered:** 2026-11-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Инфраструктурная фаза без пользовательских фич: фиксация ADR выбора стека (выбор сделан пользователем), скелет модульного монолита Django, docker-compose (PostgreSQL 18 + Redis + app), CI (lint / typecheck / tests), механизм миграций, health-check. Разблокирует все последующие фазы.

</domain>

<decisions>
## Implementation Decisions

### Стек (user gate — выбрал пользователь)
- **D-01:** Стек — Вариант B: **Python / Django 5.2 LTS + Django REST Framework**; **PostgreSQL 18** — единственная RDBMS; **Redis 8** — кэш/сессии/лимиты. Решение принял пользователь явно из вариантов A/B/C research'а (правило AGENTS.md и критерий приёмки №1 фазы). — **Reversibility:** one-way — после появления миграций и кода смена стека означает переписывание проекта.
- **D-02:** **Django Admin** принимается как админ-слой: обе админ-CRUD сущности PRD (рубрикатор, города) и будущая модерация (Phase 9) покрываются админкой; кастомная админка в v1 не строится — причина выбора варианта B.
- **D-03:** SSR через **Django templates** для SEO-страниц (фазы 5–6); JSON API через DRF — точечно (поиск, мессенджер, динамические формы). SPA-фронтенд не строим. — **Reversibility:** costly — переход на SPA-архитектуру затронет все шаблоны и клиентский слой.

### Структура репозитория
- **D-04:** Единая монорепа модульного монолита: один Django-проект с приложениями-модулями по границам домена (`accounts`, `catalog`, `geo`, `listings`, `search`, `messaging`, `moderation`) — граница модуля = владение своими таблицами (модульный монолит из ARCHITECTURE.md). — **Reversibility:** costly — перегруппировка приложений затрагивает импорты и миграции.

### Инфраструктура и tooling
- **D-05:** docker-compose: **PostgreSQL 18 + Redis 8 + Django app (gunicorn) + health-check**; объектное хранилище (MinIO/S3) НЕ включается — добавляется в Phase 5 (фотографии).
- **D-06:** CI — **GitHub Actions**: ruff (lint) + mypy (typecheck, non-strict на старте) + pytest (tests) на каждый пуш/PR; упавшая ступень краснит пайплайн (критерий №3).
- **D-07:** Миграции — нативные **Django migrations**; первая миграция воспроизводимо накатывается на чистую базу (критерий №4).
- **D-08:** Python 3.12+ (образ `python:3.12-slim` или 3.13 при подтверждённой поддержке Django 5.2); WSGI/gunicorn достаточно — ASGI только при realtime (v2+, REAL-01).

### Agent's Discretion
- Точные версии второстепенных зависимостей (сверка с research), структура settings (base/dev/prod), конфигурация линтеров, способ раздачи статики (WhiteNoise vs nginx) — усмотрение планировщика/executor'а.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project planning
- `.planning/PROJECT.md` — контекст проекта, ограничения, NFR (1M пользователей, лимиты 10/128/512, hard delete)
- `.planning/REQUIREMENTS.md` — 33 требования v1 (фаза 1 прямых REQ не имеет — инфраструктурная)
- `.planning/ROADMAP.md` § «Phase 1» — цель и 4 критерия приёмки фазы
- `docs/PRD.md` — исходный PRD (русский)

### Research (версии проверены, HIGH)
- `.planning/research/STACK.md` — варианты A/B/C; выбран B: версии Django 5.2 LTS, PostgreSQL 18, Redis 8.10 и обоснования
- `.planning/research/ARCHITECTURE.md` — модульный монолит, границы компонентов, порядок сборки
- `.planning/research/SUMMARY.md` § Implications for Roadmap — правило инвариантов и порядок фаз

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Нет — greenfield: исходного code нет (только `docs/`, `.planning/`, `.opencode/`).

### Established Patterns
- Правила репозитория: Conventional Commits, ветки `feat/``fix/`"chore/`, AGENTS.md обновляется тем же коммитом, что приносит тулинг/структуру.

### Integration Points
- `.opencode/` — конфигурация OpenCode/GSD (не часть приложения).

</code_context>

<specifics>
## Specific Ideas

- Пользователь выбрал вариант B именно из-за Django Admin: рубрикатор и справочник городов — две админ-CRUD сущности PRD, закрываемые админкой «почти бесплатно».

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 1-Фундамент — выбор стека и скелет проекта*
*Context gathered: 2026-11-18 (auto mode; stack — явный выбор пользователя)*
