---
phase: 01-fundament-vybor-steka-i-skelet-proekta
verified: 2026-04-01T12:01:00Z
status: human_needed
score: 21/22 must-haves verified
covered_files: [".dockerignore", ".env.example", ".gitattributes", ".github/workflows/ci.yml", ".gitignore", ".planning/phases/01-fundament-vybor-steka-i-skelet-proekta/01-01-PLAN.md", ".planning/phases/01-fundament-vybor-steka-i-skelet-proekta/01-01-SUMMARY.md", ".planning/phases/01-fundament-vybor-steka-i-skelet-proekta/01-02-PLAN.md", ".planning/phases/01-fundament-vybor-steka-i-skelet-proekta/01-02-SUMMARY.md", ".planning/phases/01-fundament-vybor-steka-i-skelet-proekta/01-03-PLAN.md", ".planning/phases/01-fundament-vybor-steka-i-skelet-proekta/01-03-SUMMARY.md", ".planning/phases/01-fundament-vybor-steka-i-skelet-proekta/01-04-PLAN.md", ".planning/phases/01-fundament-vybor-steka-i-skelet-proekta/01-04-SUMMARY.md", "AGENTS.md", "Dockerfile", "README.md", "apps/__init__.py", "apps/accounts/__init__.py", "apps/accounts/apps.py", "apps/catalog/__init__.py", "apps/catalog/apps.py", "apps/core/__init__.py", "apps/core/apps.py", "apps/core/views.py", "apps/geo/__init__.py", "apps/geo/apps.py", "apps/listings/__init__.py", "apps/listings/apps.py", "apps/messaging/__init__.py", "apps/messaging/apps.py", "apps/moderation/__init__.py", "apps/moderation/apps.py", "apps/search/__init__.py", "apps/search/apps.py", "compose.yaml", "config/__init__.py", "config/settings/__init__.py", "config/settings/base.py", "config/settings/dev.py", "config/settings/prod.py", "config/settings/test.py", "config/urls.py", "config/wsgi.py", "docs/adr/0001-choice-of-stack.md", "entrypoint.sh", "manage.py", "pyproject.toml", "requirements/base.txt", "requirements/dev.txt", "scripts/verify_bootstrap.cmd", "scripts/verify_bootstrap.sh", "static/css/site.css", "templates/base.html", "templates/home.html", "tests/__init__.py", "tests/conftest.py", "tests/test_health.py"]
covered_digest: "v4:sha256:097426778882d5de0df7989041086122885cc33fbebd54b6e097ae39c8767671"
behavior_unverified: 1 # ⚠️ PRESENT_BEHAVIOR_UNVERIFIED — 503-ветка /healthz при отказе зависимости (подробности ниже)
overrides_applied: 0
behavior_unverified_items:
  - truth: "GET /healthz возвращает 503 при недоступности любой зависимости (деградационная половина истины плана 01-02; 200-половина проверена поведенчески в этой сессии)"
    test: "Остановить одну из зависимостей (docker compose stop db ЛИБО stop cache) и выполнить GET http://localhost:8000/healthz; затем вернуть зависимость и повторить"
    expected: "При остановленной зависимости — HTTP 503, тело вида {\"status\": \"fail\", ...}, без версий/хостов/DSN; после восстановления — снова 200 {\"status\": \"ok\", \"checks\": {...}}"
    why_human: "Код ветки присутствует и подключён (apps/core/views.py:24–25 — except Exception → JsonResponse 503), но ни один тест не исполняет отказ зависимости (в tests/ только 200-пути; status vocabulary Step 3 требует исполнивший переход тест, а не ручной curl). Проверка наличия не видит поведение при отказе; спот-чеки верификатора не мутируют состояние стека. SUMMARY 01-02 сам признаёт ветку непокрытой"
human_verification:
  - test: "Уронить зависимость и проверить /healthz → 503"
    expected: "503 {\"status\": \"fail\"} без раскрытия внутренностей; после подъёма зависимости — 200 ok"
    why_human: "Единственная ветка кода фазы без теста; требует управляемого отказа сервиса (наличие кода ≠ поведение при отказе)"
  - test: "Запушить ветку chore/skeleton в origin и дождаться первого прогона CI на GitHub Actions"
    expected: "Job check зелёный поимённо: Lint (ruff) → Typecheck (mypy) → Migrations drift check → Tests (coverage run -m pytest); actions/checkout@v7 и actions/setup-python@v7 резолвятся"
    why_human: "Внешний CI-сервис; подтверждено в этой сессии: на origin только main (git branch -r — origin/HEAD → origin/main, ветка не запушена, первый прогон ещё не мог произойти), gh CLI на хосте отсутствует, локально workflow неисполним. Все 4 команды ступеней зеркально доказаны зелёными в этой сессии (см. Behavioral Spot-Checks)"
  - test: "Решить расхождение: Phase 1 имеет Mode: mvp в ROADMAP, но цель фазы — не User Story (gsd user-story.validate → valid=false, проверено детерминированно в этой сессии)"
    expected: "Либо переформулировать цель фазы командой /gsd-mvp-phase 1 (формат «As a…, I want to…, so that…»), либо осознанно принять стандартную goal-backward верификацию (выполнена в этом отчёте) и/или снять режим для инфраструктурных фаз"
    why_human: "Процессное решение владельца репозитория; верификатор не изменяет ROADMAP. Замечание: Mode: mvp стоит на всех 10 фазах ROADMAP, включая приёмочную фазу 10 — похоже на сквозной маркер, а не на осознанный MVP-срез фазы 1"
---

# Phase 1: Фундамент — выбор стека и скелет проекта — Verification Report

**Phase Goal:** Стек выбран явным решением пользователя и зафиксирован ADR; репозиторий-скелет модульного монолита собирается, проходит CI и поднимается одной командой
**Verified:** 2026-04-01T12:01:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Предыдущая верификация и неизменность кодовой базы

В каталоге фазы существовал предыдущий `01-VERIFICATION.md` (status: human_needed, score 21/22, **без** секции `gaps:` — по Step 0 это initial-режим, не re-verification). Все поведенческие доказательства ниже **переисполнены верификатором в этой сессии заново**, а не унаследованы. Fingerprint покрытия пересчитан: `covered_digest` совпал побайтно с предыдущим (`09742677…7671`), рабочее дерево чистое (только untracked-артефакты: `.idea/`, прошлый отчёт, кэш research, state.json), HEAD не сместился (e133bc2) — **кодовая база не менялась между верификациями**; тем не менее ни одно утверждение не принято на веру.

## MVP Mode: расхождение формата цели

ROADMAP помечает фазу `Mode: mvp`, однако `gsd query user-story.validate` на цели фазы вернул **`valid: false`** (цель «Стек выбран явным решением пользователя…» не является User Story формата «As a…, I want to…, so that…»). По правилу MVP-режима верификация против не-User-Story цели не проводится — User Flow Coverage был бы низкокачественным. Во исполнение прямого приказа оркестратора («Verify phase 01 goal achievement») выполнена **стандартная goal-backward верификация** по контракту SC-1..SC-4 (планы фазы — обычные execute-планы, контракт однозначен), а расхождение вынесено на решение владельца (Human Verification п. 3). Результат `valid: false` получен централизованным гейтом, не инлайн-регэкспом.

## Goal Achievement

### Observable Truths

Дедупликация: истины планов, дословно повторяющие SC ROADMAP (T1↔SC-1, T10↔SC-4, T17↔SC-3), слиты со SC-строками; T8 плана 01-02 разделена на 200-половину (T8a) и 503-половину (T8b) — статусы разные. Все «поведенческие» вердикты в этой таблице опираются на исполнения **этой сессии** (см. Behavioral Spot-Checks и Probe Execution).

| #   | Truth | Status | Evidence |
| --- | ----- | ------ | -------- |
| 1 | **SC-1**: В репозитории лежит ADR с явным выбором стека из вариантов A/B/C и обоснованием — выбор сделал пользователь, а не агент | ✓ VERIFIED | `docs/adr/0001-choice-of-stack.md` прочитан целиком: Status **Accepted**; строка 17 «Выбор из вариантов A/B/C сделал **пользователь**»; Decision — Вариант B (Django 5.2 LTS + DRF, PostgreSQL 18, Redis 8) + состав D-01…D-08; Alternatives A/C с причинами отклонения пользователем; Consequences (одноразовая dev-БД + `down -v` для Phase 2, пин mypy 1.19.1 в диапазоне django-stubs `<1.20`). Первоисточник — D-01…D-08 из 01-CONTEXT.md:17–28 (сверено) |
| 2 | **SC-2**: Свежий клон поднимается одной командой: docker-compose запускает PostgreSQL и Redis, приложение отвечает на health-check | ✓ VERIFIED | **Поведенчески, этой сессией**: probe `scripts\verify_bootstrap.cmd` исполнен верификатором — `down -v` (Volume pgdata Removed) → `up -d --build --wait` → db/cache `Healthy` → web `Healthy` → `curl /healthz` → `{"status": "ok", "checks": {"db": "ok", "cache": "ok"}}` → **BOOTSTRAP_OK**, exit 0. `compose.yaml:40–45` — depends_on `condition: service_healthy` обоих |
| 3 | **SC-3** (+T17): CI на каждый пуш/PR: ruff → mypy → makemigrations --check → pytest, отдельными именованными ступенями; падение ступени краснит пайплайн | ✓ VERIFIED | `.github/workflows/ci.yml` прочитан: `on: [push, pull_request]` (:5); отдельные именованные steps Lint (:50)/Typecheck (:52)/Migrations drift check (:55, ДО pytest)/Tests (:58) — в GH Actions падение step ≥ job red поимённо. Все 4 команды зеркально исполнены зелёно в контейнере этой сессией. Фактический первый прогон на GitHub — внешний факт, ветка не запушена (git branch -r: только origin/main) → Human Verification п. 2 |
| 4 | **SC-4** (+T10): Механизм миграций работает: первая миграция воспроизводимо накатывается на чистую базу | ✓ VERIFIED | **Поведенчески, этой сессией**: probe сбросил том pgdata (`Volume ai-pet-project_pgdata Removed`), entrypoint применил миграции на подъёме, `migrate --check` — «No migrations to apply» (exit 0) на чистом томе, `showmigrations` — все строки admin (3)/auth (12)/contenttypes (2)/sessions (1) `[X]` |
| 5 | T2 (01-01): Все 14 зависимостей запинены точно (`==`), включая mypy==1.19.1 внутри диапазона django-stubs 5.2.9 | ✓ VERIFIED | `requirements/base.txt` прочитан — 7 пинов `==` (Django==5.2.19 … django-environ==0.14.0); `requirements/dev.txt` — 7 пинов `==` (pytest==9.2.0 … factory_boy==3.3.3; mypy==1.19.1, django-stubs==5.2.9); итого 14, лишних пакетов нет |
| 6 | T3 (01-01): dev.txt начинается с `-r base.txt` и добавляет pytest/pytest-django/ruff/mypy/django-stubs/coverage/factory_boy | ✓ VERIFIED | `requirements/dev.txt:1` — `-r base.txt`; строки 2–8 — ровно перечисленный набор |
| 7 | T4 (01-01): `.env` в `.gitignore`; `.env.example` — имена переменных с безопасными dev-дефолтами, без реальных секретов | ✓ VERIFIED | `.gitignore:1` — `.env`; `git status --porcelain` не содержит `.env` (игнорируется; сам файл не читался — гард секретов). `.env.example` прочитан: 8 переменных, значения-заглушки (`dev-insecure-secret-key-change-me`, `classifieds-dev-only`) |
| 8 | T5 (01-01): `.gitattributes` содержит `* text=auto eol=lf` | ✓ VERIFIED | `.gitattributes:1` — дословно |
| 9 | T6 (01-01): pyproject.toml — `[tool.pytest]` с `DJANGO_SETTINGS_MODULE = "config.settings.test"` (native TOML) + конфиги ruff/mypy/django-stubs | ✓ VERIFIED | `pyproject.toml:1–13` прочитан — все четыре секции; `[tool.pytest]` native TOML (pytest 9+); pytest==9.2.0 запинован и тесты реально идут (`2 passed`) — формат валиден |
| 10 | T7 (01-02): docker compose up: PostgreSQL 18 и Redis 8, web стартует только после service_healthy обоих | ✓ VERIFIED | `compose.yaml` прочитан: db `postgres:18-alpine` (:3), cache `redis:8-alpine` (:25), web depends_on db+cache `condition: service_healthy` + `restart: true` (:40–45); **поведенчески** — вывод probe этой сессии: db/cache Waiting→Healthy, web стартует после и сам становится Healthy |
| 11 | T8a (01-02): GET /healthz возвращает 200 с JSON status ok при живых БД и кэше, без раскрытия внутренностей | ✓ VERIFIED | **Поведенчески, этой сессией**: `curl -fsS /healthz` → `{"status": "ok", "checks": {"db": "ok", "cache": "ok"}}` (и на живом стеке, и в probe на чистом томе); `tests/test_health.py::test_healthz_ok` — value-ассерты status/checks.db/checks.cache — passing (`2 passed`). В ответе только status/checks — без версий/хостов/DSN (T-01-03, сверено по коду views.py) |
| 12 | T8b (01-02): GET /healthz возвращает 503 при недоступности любой зависимости | ⚠️ PRESENT_BEHAVIOR_UNVERIFIED | Код присутствует и подключён (`apps/core/views.py:24–25` — except Exception → JsonResponse 503 с `{"status": "fail"}`), но ни один тест не исполняет отказ зависимости (tests/test_health.py — только 200-пути; переход state-transition требует исполнившего его теста) → behavior_unverified_items + Human Verification п. 1 |
| 13 | T9 (01-02): GET / отдаёт SSR-страницу (Django templates) со счётчиком, растущим при перезагрузке — реальный write+read в Redis | ✓ VERIFIED | **Поведенчески, этой сессией**: два последовательных `curl /` → `<p id="hit-counter">Просмотров: 2</p>` → `Просмотров: 3</p>` (инкремент живьём); после сброса стека probe'ом — «Просмотров: 1» (ключ `core:home:hits` рождается заново — доказательство реального Redis round-trip). `tests/test_health.py::test_home_counter_increments` — behavioral-ассерт `second == first + 1` — passing. Рендер: `templates/home.html:8` — `{{ hits }}` из контекста view (views.py:37) |
| 14 | T11 (01-02): docker compose run --rm web pytest -x -q зелёный в контейнере | ✓ VERIFIED | **Поведенчески, этой сессией**: `2 passed in 2.39s` (реальные db/cache из compose-сети) |
| 15 | T12 (01-03): Все 7 доменных приложений существуют и зарегистрированы в INSTALLED_APPS; моделей в них нет | ✓ VERIFIED | `config/settings/base.py:44–50` прочитано — apps.accounts…apps.moderation (8 прикладных с apps.core); glob `apps/**/models.py` — **0 файлов**; migrations/ тоже нет (Pattern 4). INSTALLED_APPS реально работает — Django поднялся и сделал миграции на эти приложения (probe) |
| 16 | T13 (01-03): makemigrations --check --dry-run проходит — дрейфа нет | ✓ VERIFIED | **Поведенчески, этой сессией**: «No changes detected», exit 0 |
| 17 | T14 (01-03): config/settings/prod.py валиден: DEBUG=False, ALLOWED_HOSTS из env | ✓ VERIFIED | `prod.py` прочитан: DEBUG=False (:9), ALLOWED_HOSTS=env.list("DJANGO_ALLOWED_HOSTS", default=[localhost,127.0.0.1,web]) (:14–17), SECURE_CONTENT_TYPE_NOSNIFF (:20); **поведенчески**: `docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py check` — «System check identified no issues (0 silenced)», exit 0 (моя сессия) |
| 18 | T15 (01-03): README.md объясняет подъём одной командой | ✓ VERIFIED | README.md: `docker compose up -d --build --wait` (:33), `curl http://localhost:8000/healthz` (:39), приёмка `scripts\verify_bootstrap.cmd` / `.sh` (:45), правило пересборки образа (:51) |
| 19 | T16 (01-03): AGENTS.md фиксирует реальные проверенные команды | ✓ VERIFIED | AGENTS.md: docker-first команды (pytest :11 и др.), состав CI (:3 — «first run happens on the first push of a branch» — честная формулировка, зелёность не заявляется); каждая команда исполнена зелёно в этой верификации (up — probe; pytest/ruff/mypy/healthz — спот-чеки) |
| 20 | T18 (01-04): CI-ступени сервисов: postgres:18 и redis:8 с health-cmd pg_isready; тест-БД из миграций | ✓ VERIFIED | `ci.yml:16–31` прочитано — services postgres (image postgres:18, --health-cmd pg_isready, ports 5432) и redis:8-alpine (ports 6379); тест-БД из миграций — поведенчески подтверждено прогоном pytest в контейнере этой сессией (тот же механизм pytest-django; job env ci.yml:38 явно ставит DJANGO_SETTINGS_MODULE=config.settings.test) |
| 21 | T19 (01-04): Все CI-ступени зеркально зелёные локально через docker compose run --rm web | ✓ VERIFIED | **Поведенчески, исполнены верификатором в этой сессии**: ruff «All checks passed!», mypy «Success: no issues found in 30 source files», makemigrations --check --dry-run «No changes detected», pytest «2 passed» |
| 22 | T20 (01-04): Workflow использует least-privilege permissions (contents: read) и кэш pip (cache-dependency-path requirements/*.txt) | ✓ VERIFIED | `ci.yml:8–9` — permissions contents: read; `ci.yml:44–45` — cache 'pip' + cache-dependency-path requirements/*.txt |

**Score:** 21/22 truths verified (1 present, behavior-unverified)

### Required Artifacts

Инструментальная проверка `verify.artifacts` по 4 планам: **17/18 passed** (01-01: 6/6; 01-02: 6/7; 01-03: 5/5; 01-04: 1/1). Единственный инструментальный промах разобран вручную ниже.

| Artifact | Expected | Status | Details |
| -------- | -------- | ------ | ------- |
| `docs/adr/0001-choice-of-stack.md` | ADR выбора стека (SC-1), contains "Consequences" | ✓ VERIFIED | passed; 53 строки, все секции прочитаны |
| `requirements/base.txt` | Рантайм-пины, contains "Django==5.2.19" | ✓ VERIFIED | passed; 7 пинов |
| `requirements/dev.txt` | Dev-зависимости, contains "mypy==1.19.1" | ✓ VERIFIED | passed; -r base.txt + 7 |
| `pyproject.toml` | Дом конфигов тулинга, contains "[tool.pytest]" | ✓ VERIFIED | passed; 4 секции |
| `.gitattributes` | eol=lf | ✓ VERIFIED | passed |
| `.env.example` | Шаблон env, contains "DJANGO_SECRET_KEY" | ✓ VERIFIED | passed; без реальных секретов |
| `apps/core/views.py` | healthz + home, contains "healthz" | ✓ VERIFIED | passed; SELECT 1 + cache ping + счётчик; 503-ветка присутствует |
| `config/settings/base.py` | 12-factor, contains "django_redis.cache.RedisCache" | ✓ VERIFIED | passed; SECRET_KEY/DATABASES/CACHES только из env |
| `compose.yaml` | Оркестрация, contains "service_healthy" | ✓ VERIFIED | passed; healthchecks всех трёх сервисов |
| `Dockerfile` | python:3.13-slim + requirements + entrypoint | ✓ VERIFIED | passed; + нормализация режимов .py (EXE002) |
| `entrypoint.sh` | migrate → collectstatic → exec gunicorn, contains "gunicorn" | ✓ VERIFIED | passed; + ветка exec "$@" для one-off команд |
| `tests/test_health.py` | Интеграция /healthz и /, contains "healthz" | ✓ VERIFIED | passed; 2 теста, value+behavioral ассерты |
| `scripts/verify_bootstrap.cmd` | Однокомандная приёмка, contains "verify" | ✓ VERIFIED (примечание) | Инструментальный паттерн-чек FAILED: литерал `verify` отсутствует **в теле** файла (только в имени). Ручная проверка: 31 строка прочитана — полный 7-шаговый сценарий (down -v → up --wait → curl ×2 → migrate --check → showmigrations → BOOTSTRAP_OK), errorlevel-гейт после каждого шага; **исполнен верификатором — exit 0, BOOTSTRAP_OK**; wired — README.md:45 и AGENTS.md ссылаются. **Не стаб** — расхождение метаданных плана (`contains: "verify"`), не функциональный дефект |
| `apps/accounts/apps.py` | AccountsConfig, contains "apps.accounts" | ✓ VERIFIED | passed; INSTALLED_APPS реально резолвит (стек поднят) |
| `apps/moderation/apps.py` | ModerationConfig, contains "apps.moderation" | ✓ VERIFIED | passed |
| `config/settings/prod.py` | DEBUG=False, ALLOWED_HOSTS, contains "ALLOWED_HOSTS" | ✓ VERIFIED | passed; + check под prod — 0 issues (моя сессия) |
| `README.md` | Быстрый старт, contains "compose" | ✓ VERIFIED | passed |
| `AGENTS.md` | Проверенные команды, contains "pytest" | ✓ VERIFIED | passed |

### Key Link Verification

`verify.key-links` по 4 планам: **13/14 verified** (01-01: 2/2; 01-02: 5/6; 01-03: 3/3; 01-04: 3/3). Единственный промах — опосредованная связь, доказана поведенчески.

| From | To | Via | Status | Details |
| ---- | -- | --- | ------ | ------- |
| requirements/dev.txt | requirements/base.txt | `-r base.txt` | ✓ WIRED | Pattern found in source (dev.txt:1 прочитан) |
| pyproject.toml | config/settings/test.py | DJANGO_SETTINGS_MODULE | ✓ WIRED | Pattern found (pyproject.toml:2 прочитан; test.py существует) |
| config/urls.py | apps/core/views.py | импорт healthz/home | ✓ WIRED | urls.py:5 — `from apps.core.views import healthz, home` (прочитан) |
| apps/core/views.py | config/settings/base.py | cache→Redis, connection→PG | ✓ WIRED | views.py:1–2 импортирует cache/connection; base.py:26–31 CACHES django_redis + DATABASES env.db (оба прочитаны) |
| entrypoint.sh | config/wsgi.py | exec gunicorn config.wsgi | ✓ WIRED | entrypoint.sh:14 — `exec gunicorn config.wsgi:application` (прочитан) |
| compose.yaml | Dockerfile | build "." | ✓ WIRED | compose.yaml:36 — `build: "."` (прочитан) |
| Dockerfile | requirements/dev.txt | pip install -r | ✓ WIRED | Dockerfile:14 (прочитан) |
| tests/test_health.py | config/settings/test.py | pyproject [tool.pytest] DJANGO_SETTINGS_MODULE | ✓ WIRED (опосредованно) | Инструмент: pattern not found в source/target — связь идёт **через pyproject.toml** (:1–2), а не напрямую между файлами. **Поведенческое доказательство этой сессии**: pytest в контейнере исполняется под test-настройками против реальных db/cache — `2 passed`; ci.yml:38 дополнительно ставит тот же модуль явно |
| config/settings/base.py | apps/accounts/apps.py | INSTALLED_APPS | ✓ WIRED | base.py:44 (прочитан); стек с зарегистрированными приложениями поднялся |
| config/settings/prod.py | config/settings/base.py | from .base import * | ✓ WIRED | prod.py:6 (прочитан); check под prod exit 0 |
| README.md | scripts/verify_bootstrap.cmd | ссылка на приёмку | ✓ WIRED | README.md:45 (grep) |
| .github/workflows/ci.yml | requirements/dev.txt | pip install + cache-dependency-path | ✓ WIRED | ci.yml:47, :45 (прочитан) |
| .github/workflows/ci.yml | pyproject.toml | конфиги ступеней из корня | ✓ WIRED | ci.yml:2 (комментарий) + автодискавери ruff/mypy/pytest; ступени доказаны зелёными локально на тех же конфигах |
| .github/workflows/ci.yml | config/settings/test.py | DJANGO_SETTINGS_MODULE в job env | ✓ WIRED | ci.yml:38 (прочитан) |

### Data-Flow Trace (Level 4)

Фаза рендерит одну динамическую страницу и один JSON-эндпоинт — трассировка выполнена для них; источники — реальные, не статические заглушки.

| Artifact | Data Variable | Source | Produces Real Data | Status |
| -------- | ------------- | ------ | ------------------ | ------ |
| templates/home.html | `{{ hits }}` | apps/core/views.py:32–36 → `cache.incr("core:home:hits")` → Redis (django_redis) | Да — значение меняется между запросами (2→3 живьём; 1 после сброса стека) | ✓ FLOWING |
| apps/core/views.py (healthz) | `checks` | `cursor.execute("SELECT 1")` (PostgreSQL, views.py:19–20) + `cache.set("healthz:ping", …)` (Redis, :22) | Да — JSON с db/cache ok подтверждён curl'ом при живых зависимостях | ✓ FLOWING |
| apps/core/views.py (home) | hits-контекст | Redis-счётчик, ветки incr/set | Да | ✓ FLOWING |

### Behavioral Spot-Checks

Все проверки исполнены верификатором в этой сессии (стек поднят; команды ≤10 с, кроме probe). Полный сьют (pytest) запущен один раз; отдельные tests поимённо не фильтровались.

| Behavior | Command | Result | Status |
| -------- | ------- | ------ | ------ |
| /healthz 200 + ok при живых зависимостях | `curl.exe -fsS http://localhost:8000/healthz` | `{"status": "ok", "checks": {"db": "ok", "cache": "ok"}}` | ✓ PASS |
| Счётчик растёт между запросами (Redis round-trip) | `curl /` ×2 | «Просмотров: 2» → «Просмотров: 3» | ✓ PASS |
| Неприменённых миграций нет | `docker compose run --rm web python manage.py migrate --check` | «No migrations to apply.», exit 0 | ✓ PASS |
| Дрейф моделей/миграций отсутствует | `docker compose run --rm web python manage.py makemigrations --check --dry-run` | «No changes detected», exit 0 | ✓ PASS |
| Wave 0 тесты в контейнере (полный сьют, 1 прогон) | `docker compose run --rm web pytest -x -q` | `2 passed in 2.39s` | ✓ PASS |
| CI-зеркало: lint | `docker compose run --rm web ruff check .` | «All checks passed!» | ✓ PASS |
| CI-зеркало: типы | `docker compose run --rm web mypy .` | «Success: no issues found in 30 source files» | ✓ PASS |
| Прод-настройки валидны | `docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.prod web python manage.py check` | «System check identified no issues (0 silenced)», exit 0 | ✓ PASS |
| Тестов со skip-маркерами нет | чтение tests/ (26 строк целиком) | skip/xfail/pytest.mark.skip — отсутствуют | ✓ PASS |

### Probe Execution

| Probe | Command | Result | Status |
| ----- | ------- | ------ | ------ |
| `scripts/verify_bootstrap.cmd` | `scripts\verify_bootstrap.cmd` (из корня репозитория, исполнен верификатором) | `down -v` (том pgdata Removed) → `up -d --build --wait` (db/cache Healthy → web Healthy) → `curl /healthz` → `{"status": "ok", "checks": {"db": "ok", "cache": "ok"}}` → `curl /` содержит hit-counter «Просмотров: 1» → `migrate --check` exit 0 → `showmigrations` все `[X]` (admin 3, auth 12, contenttypes 2, sessions 1) → **BOOTSTRAP_OK**; exit 0 | PASS |
| `scripts/verify_bootstrap.sh` | — | Unix-близнец исполненного .cmd: тот же 7-шаговый сценарий, маркер BOOTSTRAP_OK — подтверждён чтением файла (строки 7–26); на Windows-хосте нет sh/bash | SKIP (платформенный близнец .cmd исполнен) |

### Requirements Coverage

Фаза не имеет прямых v1-требований (REQUIREMENTS.md:147: «Phase 1 — инфраструктурная фаза без прямых требований»; traceability мапит 33/33 REQ-ID на фазы 2–9). Orphaned-требований нет — REQUIREMENTS.md не относит к фазе 1 ни одного ID. Якоря приёмки — SC-1..SC-4 из ROADMAP (roadmap contract, запрошен `roadmap.get-phase 1`); заявки SUMMARY-фронтmatter'ов проверены против кодовой базы:

| SC | Заявлен в планах | Статус по факту | Evidence |
| ----- | ---------------- | --------------- | -------- |
| SC-1 | 01-01 (`requirements: [SC-1]`) | ✓ SATISFIED | Truth #1 (ADR прочитан) |
| SC-2 | 01-02 (`[SC-2, SC-4]`), 01-03 (`[SC-2]`) | ✓ SATISFIED | Truth #2 (probe, моя сессия) |
| SC-3 | 01-04 (`[SC-3, SC-4]`) | ✓ SATISFIED (структурно + локальное зеркало; первый GitHub-прогон — human item) | Truth #3 |
| SC-4 | 01-02, 01-04 | ✓ SATISFIED | Truth #4 (probe, чистый том, моя сессия) |

Все 4 SC-якоря покрыты планами и подтверждены; дублирующих/конфликтующих заявок нет.

### Decision Coverage

CLI-гейт `check.decision-coverage-verify` скипнулся («CONTEXT.md missing» — гейт ищет файл без префикса, на диске `01-CONTEXT.md`; quirk именования, не отсутствие артефакта). Проверено вручную: D-01…D-08 из 01-CONTEXT.md:17–28 **все 8 материализованы** — D-01→ADR-0001 Decision (:21); D-02→config/urls.py:13 admin-роут; D-03→templates/home.html SSR; D-04→7 приложений в INSTALLED_APPS (base.py:44–50); D-05→compose.yaml (postgres:18+redis:8+gunicorn+healthchecks); D-06→.github/workflows/ci.yml (ruff/mypy/pytest поимённо); D-07→миграции применились на чистом томе (probe); D-08→Dockerfile python:3.13-slim + gunicorn WSGI. **8/8 honored.**

### Test Quality Audit

| Test File | Linked SC | Active | Skipped | Circular | Assertion Level | Verdict |
|-----------|-----------|--------|---------|----------|-----------------|---------|
| tests/test_health.py::test_healthz_ok | SC-2 | 1 | 0 | 0 | Value (status=="ok", checks.db=="ok", checks.cache=="ok") | ✓ доказателен |
| tests/test_health.py::test_home_counter_increments | SC-2/D-03 | 1 | 0 | 0 | Behavioral (second == first + 1) | ✓ доказателен |

Disabled-тестов на требования: 0. Циркулярных паттернов: 0 (файлы тестов ничего не пишут). Провенанс ожидаемых значений: спецификация контракта /healthz, не вывод системы. Непокрытая error-ветка: одна — 503-деградация (T8b, behavior_unverified).

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| — | — | Долг-маркеры (TBD/FIXME/XXX/TODO/HACK/PLACEHOLDER), placeholder-фразы, пустые реализации (`return null/{}/[]`) в файлах реализации фазы (apps/, config/, tests/, scripts/, templates/, static/, requirements/, docs/adr/, корневые конфиги): **не найдены** (findstr-скан этой сессии) | — | — |

Зафиксированные в SUMMARY отклонения проверены в коде этой сессией — все обоснованы и не нарушают ни одну истину/SC (Info):

1. **compose.yaml**: хост-порты db/cache `127.0.0.1:15432/16379` вместо 5432/6379 (:15, :29 — с комментариями) — конфликт с локальными сервисами разработчика; loopback-only сохранён (T-01-04), внутренняя сеть не изменилась (db:5432/cache:6379). SC-2 номеров портов не требует.
2. **compose.yaml**: `pgdata:/var/lib/postgresql` (:11) — требование postgres:18+ (versioned layout, PR #1259); probe подтверждает работоспособность на чистом томе.
3. **entrypoint.sh**: ветка `exec "$@"` (:10–12) — делает исполнимыми предписанные one-off команды (`compose run web pytest` и т.п.); поведенчески доказано всеми спот-чеками.
4. **config/urls.py**: алиас `path("healthz", healthz)` без слэша (:11) — пробы зондов получают 200 сразу, а не 301 от APPEND_SLASH; key_link-паттерн `healthz/` сохранён (:8).
5. **base.py**: явные безопасные дефолты DEBUG=False / ALLOWED_HOSTS=[] (:18–20) — deployment checklist.
6. **prod.py**: SECURE_BROWSER_XSS_FILTER не включена (:26–28 — настройка не существует в Django 5.2, удалена в 4.0); в must_haves.truths флага нет, отклонение задокументировано в файле с механизмом замены (CSP в фазах 5–6).

### Human Verification Required

1. **503-ветка /healthz при отказе зависимости**
   - **Test:** `docker compose stop db` (или `stop cache`), затем `curl -i http://localhost:8000/healthz`; вернуть зависимость, повторить.
   - **Expected:** HTTP 503, `{"status": "fail", …}`, без внутренностей; после восстановления — 200 ok.
   - **Why human:** единственная ветка кода фазы без теста; требует управляемого отказа сервиса (наличие кода ≠ поведение при отказе; спот-чеки не мутируют состояние стека).
2. **Первый прогон CI на GitHub Actions**
   - **Test:** запушить `chore/skeleton` в origin, открыть вкладку Actions.
   - **Expected:** job check зелёный поимённо (Lint/Typecheck/Migrations drift check/Tests); теги actions/checkout@v7 и actions/setup-python@v7 резолвятся.
   - **Why human:** внешний CI-сервис; подтверждено: на origin только main (ветка не запушена — прогона ещё не было), gh CLI отсутствует; локально workflow неисполним. Все 4 команды ступеней доказаны зелёными локально в этой сессии.
3. **Решение по mode: mvp vs не-User-Story цель фазы** (см. секцию MVP Mode)
   - **Test:** выбрать: `/gsd-mvp-phase 1` (переформатировать цель) ЛИБО принять стандартную верификацию / снять режим для инфраструктурных фаз.
   - **Expected:** Roadmap и режим фазы согласованы; `user-story.validate` возвращает valid=true либо режим снят.
   - **Why human:** процессное решение владельца; верификатор не редактирует ROADMAP.

### Gaps Summary

Блокирующих пробелов нет: все 4 критерия приёмки ROADMAP подтверждены (SC-2 и SC-4 — поведенчески, верификатором в этой сессии, с воспроизведением на чистом томе через приёмочный probe; SC-1 — чтением ADR; SC-3 — структурой workflow + локальным зеркалом всех ступеней), артефакты существуют/содержательны/подключены (17/18 инструментально + 1 разобран вручную — не стаб), данные реально текут (Redis-счётчик растёт живьём), долг-маркеров нет, решения CONTEXT 8/8 материализованы, требований-сирот нет.

Статус `human_needed` обусловлен тремя пунктами: (1) непокрытая тестом 503-ветка healthz (⚠️ present-behavior-unverified — код есть и подключён, поведение при отказе зависимости не исполнено ни одним тестом), (2) фактическая зелёность CI на GitHub — внешний факт, первый прогон невозможен до пуша ветки (origin содержит только main), (3) процессное расхождение `Mode: mvp` / не-User-Story цель (детерминированно: user-story.validate → false). Ни один из пунктов не является провалом истины — это предел локальной верифицируемости, требующий человека.

---

_Verified: 2026-04-01T12:01:00Z_
_Verifier: the agent (gsd-verifier)_
