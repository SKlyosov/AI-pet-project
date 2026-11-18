---
phase: 01-fundament-vybor-steka-i-skelet-proekta
plan: "03"
subsystem: infra
tags: [django, modular-monolith, app-scaffold, settings, prod-config, documentation]

requires:
  - phase: 01-fundament-vybor-steka-i-skelet-proekta/01-02
    provides: walking skeleton (Django 5.2 + compose, healthz, pytest, verify_bootstrap)
provides:
  - 7 доменных приложений-каркасов (accounts, catalog, geo, listings, search, messaging, moderation), зарегистрированных в INSTALLED_APPS — структура модульного монолита D-04 целиком
  - config/settings/prod.py — прод-контракт DEBUG=False + ALLOWED_HOSTS из env (T-01-05/T-01-06)
  - README.md (RU) и AGENTS.md с проверенными docker-first командами (SC-2 документационно)
affects: [02-accounts, 03-catalog-geo, 04-listings, 05-media, 06-public-pages, 07-search, 08-messaging, 09-moderation]

actuals:
  tokens: 3300        # chars/4 по реализованному diff (13028 символов)
  tasks: 3
  commits: 4          # git rev-list --count 5971af8..6612428
plan_head_before: 5971af85a0ae3c2ab7dde5b96c11975415ade8d2
plan_head_after: 6612428849f4c1b0b332eec916d6b07e665694e8

tech-stack:
  added: []           # T-01-SC: новых пакетов нет — только код на пинах 01-01/01-02
  patterns:
    - "Доменный каркас = пустой __init__.py + apps.py (AppConfig), без models.py/migrations — модели появляются в фазах-владельцах таблиц (Pattern 4)"
    - "Дисциплина границ D-04/Pattern 3 фиксируется docstring'ом каждого apps.py: чужие таблицы — только через сервис-функцию владельца"

key-files:
  created:
    - apps/accounts/apps.py
    - apps/catalog/apps.py
    - apps/geo/apps.py
    - apps/listings/apps.py
    - apps/search/apps.py
    - apps/messaging/apps.py
    - apps/moderation/apps.py
    - config/settings/prod.py
  modified:
    - config/settings/base.py
    - .env.example
    - README.md
    - AGENTS.md
    - Dockerfile          # отклонение Rule 3: нормализация режимов .py в образе
    - apps/core/views.py  # отклонение Rule 3: точечный noqa BLE001
    - config/settings/dev.py  # отклонение Rule 3: снят неиспользуемый noqa
    - config/settings/test.py # отклонение Rule 3: снят неиспользуемый noqa

key-decisions:
  - "D-04 материализован 7 пустыми AppConfig-каркасами: границы дёшевы, пока приложения без таблиц (Pattern 3 research'а)"
  - "SECURE_BROWSER_XSS_FILTER из плана НЕ включена: настройки нет в Django 5.2 (удалена в 4.0, проверено по django.conf.global_settings); XSS-защита шаблонов фаз 5–6 — Content-Security-Policy"
  - "env.list с list-default: строковый дефолт django-environ НЕ парсится (возвращается как одна строка) — дефолт задан списком, поведение проверено пробником в контейнере"
  - "EXE002 в образе лечится нормализацией режимов в Dockerfile (Windows build-context ставит exec-бит всем файлам; в git они 100644), а не подавлением правила"

patterns-established:
  - "Scaffold доменного app'а: __init__.py + apps.py по образцу CoreConfig, домен и дисциплина границ — в docstring класса"
  - "Наследник настроек окружения: from .base import *; переопределяется только окружение-зависимое (dev/prod/test симметричны)"

requirements-completed: [SC-2]

coverage:
  - id: D1
    description: "Семь доменных приложений-каркасов созданы и зарегистрированы в INSTALLED_APPS (D-04), миграционного дрейфа нет"
    requirement: SC-2
    verification:
      - kind: other
        ref: "findstr /C:apps.accounts config\\settings\\base.py && findstr /C:apps.moderation config\\settings\\base.py"
        status: pass
      - kind: other
        ref: "docker compose run --rm web python manage.py makemigrations --check --dry-run (No changes detected)"
        status: pass
      - kind: integration
        ref: "docker compose run --rm web pytest -x -q (2 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "config/settings/prod.py валиден: DEBUG=False, ALLOWED_HOSTS из env, SECURE_CONTENT_TYPE_NOSNIFF; .env.example дополнен DJANGO_ALLOWED_HOSTS"
    verification:
      - kind: other
        ref: "docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py check (0 issues)"
        status: pass
      - kind: other
        ref: "findstr /C:ALLOWED_HOSTS, /C:DEBUG config\\settings\\prod.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "README (RU) и AGENTS.md фиксируют проверенные команды: подъём, тесты, линт, типы, приёмка скелета"
    verification:
      - kind: other
        ref: "findstr-гейты: compose/verify_bootstrap в README; pytest/ruff/mypy в AGENTS.md; устаревшая строка 'nothing to build' удалена"
        status: pass
      - kind: other
        ref: "каждая задокументированная команда исполнена зелёно в контейнере этой же сессией (ruff/mypy/pytest/healthz)"
        status: pass
    human_judgment: true
    rationale: "Критерий done — «новый разработчик поднимает проект по README без вопросов» — оценка достаточности документации требует человека; дословность команд проверена автоматически."

duration: 24min
completed: 2026-11-18
status: complete
---

# Phase 1 Plan 3: Структура модульного монолита, прод-настройки и документация Summary

**7 доменных AppConfig-каркасов (D-04) в INSTALLED_APPS, prod-модуль с DEBUG=False и ALLOWED_HOSTS из env, README/AGENTS.md с зелёно проверенными docker-first командами**

## Performance

- **Duration:** 24 min
- **Started:** 2026-11-18T09:20:02Z
- **Completed:** 2026-11-18T09:44:14Z
- **Tasks:** 3
- **Files modified:** 23 (14 созданы, 9 изменены)

## Accomplishments

- Структура модульного монолита D-04 материализована: apps/core + 7 доменных каркасов, каждый — ровно `__init__.py` + `apps.py` (без моделей, Pattern 4); граница модуля = владение таблицами, дисциплина импортов зафиксирована docstring'ами
- `makemigrations --check --dry-run` зелёный на свежем образе: регистрация пустых приложений не порождает миграций и не ломает SC-4
- Прод-контракт настроек: `config/settings/prod.py` (DEBUG=False, ALLOWED_HOSTS через `env.list("DJANGO_ALLOWED_HOSTS")` со списковым дефолтом loopback+web, SECURE_CONTENT_TYPE_NOSNIFF; TLS-гейт-флаги задокументированы комментариями) — `manage.py check` под prod: 0 issues
- README (русский) и AGENTS.md фиксируют только реально исполненные команды: `docker compose up -d --build --wait`, `pytest -x -q`, `ruff check .`, `mypy .`, `scripts\verify_bootstrap.cmd|sh`; фиксирован факт «контейнер исполняет код из образа — после правок пересобирайте»
- lint приведён к зелёному внутри образа (см. отклонения) — `ruff check .`: All checks passed; `mypy .`: 30 файлов, 0 ошибок; `pytest -x -q`: 2 passed

## Task Commits

Each task was committed atomically:

1. **Task 1: Семь доменных приложений-каркасов + регистрация (D-04)** — `b750f4d` (feat)
2. **Task 2: Прод-настройки config/settings/prod.py** — `c668ebc` (feat)
3. **Task 3: README + AGENTS.md — проверенные команды тулинга** — `6612428` (docs)
4. **Отклонение Rule 3 (до Task 3): зелёный ruff в образе** — `cf30d5b` (fix)

**Plan metadata:** см. финальный docs-коммит плана.

## Files Created/Modified

- `apps/{accounts,catalog,geo,listings,search,messaging,moderation}/__init__.py` + `apps.py` — AppConfig-каркасы доменов (модели — фазы 2–9)
- `config/settings/base.py` — INSTALLED_APPS расширен до 8 прикладных модулей
- `config/settings/prod.py` — прод-настройки (Pitfall 4, T-01-05/T-01-06)
- `.env.example` — ключ `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web`
- `README.md` — быстрый старт одной командой (SC-2), команды тестов/линта, приёмка
- `AGENTS.md` — фактический docker-first workflow вместо «nothing to build/test/lint»
- `Dockerfile`, `apps/core/views.py`, `config/settings/{dev,test}.py` — правки зелёного lint (отклонения 2–3)

## Decisions Made

- Пустые каркасы без models.py/migrations — осознанно (Pattern 4): первая доменная миграция появится в Phase 2 (custom User ДО пользовательских данных, ADR-0001)
- `SECURE_BROWSER_XSS_FILTER` не включена — настройки нет в Django 5.2 (удалена в 4.0; проверено по `django.conf.global_settings`); задокументировано в prod.py, XSS-защита шаблонов — CSP в фазах 5–6
- Дефолт `ALLOWED_HOSTS` — список (строковый дефолт `env.list` не парсится — проверено пробником в контейнере)
- EXE002 — дефект образа (Windows build-context exec-бит), лечится chmod-нормализацией в Dockerfile, а не ignore-правилом

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Докер-гейты прогонялись по устаревшему образу**
- **Found during:** Task 2 (verify `manage.py check` → ModuleNotFoundError: config.settings.prod)
- **Issue:** `docker compose run --rm web` исполняет код, запечённый в образ; гейты Task 1 (makemigrations-check, pytest) изначально прошли по образу 01-02 — без новых файлов
- **Fix:** `docker compose up -d --build --wait`; ВСЕ докер-гейты Task 1 и Task 2 перегнаны по свежему образу — зелёные
- **Files modified:** — (только пересборка)
- **Verification:** makemigrations --check «No changes detected», pytest 2 passed, prod check 0 issues
- **Committed in:** — (верификационная пересборка, коммита не требует)

**2. [Rule 1 - Bug] SECURE_BROWSER_XSS_FILTER отсутствует в Django 5.2**
- **Found during:** Task 2 (прод-настройки)
- **Issue:** план предписывал флаг, удалённый из Django в 4.0; установка была бы инертной фикцией защиты («verified facts only»)
- **Fix:** флаг не включён; в prod.py задокументированы факт удаления и будущий механизм (CSP для шаблонов фаз 5–6)
- **Files modified:** config/settings/prod.py
- **Verification:** проверка по django.conf.global_settings в контейнере; manage.py check — 0 issues
- **Committed in:** c668ebc

**3. [Rule 3 - Blocking] `ruff check .` красный (35 ошибок) — Task 3 не мог задокументировать зелёную команду**
- **Found during:** Task 3 (предварительный прогон команд для «verified facts only»)
- **Issue:** 30×EXE002 (Windows build-context ставит exec-бит всем файлам в образе; в git они 100644), 5×RUF100 (noqa F401/F403 вне активного ruleset), 1×BLE001 (штатный catch-all healthz)
- **Fix:** Dockerfile нормализует режимы .py (manage.py сохраняет exec — стандартный shebang); сняты 5 неиспользуемых noqa (dev.py ×2, test.py ×1, prod.py ×2); точечный `# noqa: BLE001` с обоснованием (контракт 503 при отказе любой зависимости, Pattern 2)
- **Files modified:** Dockerfile, apps/core/views.py, config/settings/{dev,test,prod}.py
- **Verification:** ruff — All checks passed; mypy — 30 файлов без ошибок; pytest — 2 passed; prod check — 0 issues
- **Committed in:** cf30d5b

---

**Total deviations:** 3 auto-fixed (1 bug, 2 blocking)
**Impact on plan:** Все правки — корректность и честность гейтов; объём плана не превышен (23 файла против 19 запланированных — 4 файла lint-фикса). Новых зависимостей нет (T-01-SC соблюдён).

## Issues Encountered

- Устаревший образ docker (отклонение 1) — системная ловушка «compose run ≠ свежий код»; зафиксирована в README/AGENTS.md как правило workflow («после изменения кода пересоберите образ»)

## Known Stubs

Пустые доменные приложения — НЕ заглушки, а предусмотренный планом результат (D-04/Pattern 4): каркас = граница владения таблицами; модели появятся в фазах-владельцах (accounts — Phase 2, catalog/geo — Phase 3, listings — Phase 4, search — Phase 7, messaging — Phase 8, moderation — Phase 9).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Готово к 01-04 (CI) и Phase 2 (accounts: custom User в существующем каркасе)
- Локально зелёный полный триптих ruff/mypy/pytest — CI ожидает те же команды
- Прод-настройки провалидированы `manage.py check`; `check --deploy` — в ведении CI/приёмки (research V14)

## Self-Check: PASSED

- Файлы: apps/{accounts,catalog,geo,listings,search,messaging,moderation}/apps.py, config/settings/prod.py, README.md, AGENTS.md — FOUND
- Коммиты b750f4d, c668ebc, cf30d5b, 6612428 — ancestors of HEAD (merge-base --is-ancestor)
- Коммитов от ledger-базы: 4; изменений без коммита нет

---

*Phase: 01-fundament-vybor-steka-i-skelet-proekta*
*Completed: 2026-11-18*
