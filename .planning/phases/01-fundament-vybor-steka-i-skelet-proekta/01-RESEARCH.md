# Phase 1: Фундамент — выбор стека и скелет проекта - Research

**Researched:** 2026-11-18
**Domain:** Django 5.2 модульный монолит — скелет репозитория, docker-compose (PostgreSQL 18 + Redis 8 + gunicorn), GitHub Actions CI, миграции, health-check
**Confidence:** HIGH (версии — живые запросы к PyPI + разрешение зависимостей pip-резолвером; совместимость — официальные доки с verbatim-цитатами; community-паттерны — MEDIUM/[ASSUMED])

## Summary

Стек зафиксирован пользователем (D-01…D-08 в CONTEXT.md) и исследованию не подлежит — исследован способ его собрать. Ключевой вывод: **весь набор зависимостей resolves для Python 3.13/Linux и подтверждён метаданными колёс с PyPI**. Пробное разрешение (`pip download` с `--python-version 3.13 --platform manylinux_2_28/2_17_x86_64`) успешно прошло по полному списку: Django 5.2.19 (последний патч LTS-линии 5.2), DRF 3.18.3, gunicorn 27.0.1, `psycopg[binary]` 3.3.9 (cp313-manylinux wheel существует), django-redis 7.0.0 (тянет redis-py 8.1.0), whitenoise 6.12.0, django-environ 0.14.0, pytest 9.2.0, pytest-django 4.14.0, ruff 0.17.5, django-stubs 5.2.9, coverage 7.17.3, factory_boy 3.3.3 [VERIFIED: PyPI registry].

Совместимость подтверждена первоисточниками: Django 5.2 официально поддерживает Python «3.10, 3.11, 3.12, 3.13, 3.14 (added in 5.2.8)» и «PostgreSQL 14 and higher» с рекомендацией psycopg 3 [CITED: docs.djangoproject.com/en/5.2]; DRF 3.18.3 объявляет `django>=5.2`; django-redis 7.0.0 — `Django<7.0,>=5.2` + redis-py ≥4.0.2; pytest-django 4.14.0 — `pytest>=7.0.0` с классифайером Django 5.2 [VERIFIED: wheel METADATA]. **Python 3.13 — наибольшая версия, общая для всего набора** (gunicorn 27 и django-stubs 5.2.9 заявляют максимум 3.13; 3.14 — только Django/DRF/psycopg).

Обнаружена и обезврежена единственная реальная мина совместимости: django-stubs 5.2.9 объявляет `compatible-mypy: mypy>=1.13,<1.20` — то есть **mypy 2.x вне тестируемого диапазона**; mypy нужно пинить в линии 1.19 (`mypy==1.19.1`, wheel для cp313 проверен) [VERIFIED: wheel METADATA]. Прочие выводы для планирования: layout — `config/settings/{base,dev,prod}` + `apps/<домен>`; health-check — рукописный `/healthz` (SELECT 1 + cache ping, без раскрытия внутренностей); первая миграция — никаких фейковых моделей, критерий №4 закрывается чистым `migrate` на чистом томе (contrib-миграции auth/admin/contenttypes/sessions) + `showmigrations`; CI — один job с последовательными ступенями ruff → mypy → pytest и `services:` postgres+redis.

**Primary recommendation:** собрать скелет на Python 3.13 (`python:3.13-slim` для web, `postgres:18(-alpine)` и `redis:8-alpine` для сервисов) с пинами из таблицы Standard Stack, составить `compose.yaml` с `depends_on: condition: service_healthy`, CI c `actions/setup-python@v7` + `cache: 'pip'`, и зафиксировать ADR + обновление AGENTS.md тем же коммитом, что приносит тулинг.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### the agent's Discretion
- Точные версии второстепенных зависимостей (сверка с research), структура settings (base/dev/prod), конфигурация линтеров, способ раздачи статики (WhiteNoise vs nginx) — усмотрение планировщика/executor'а.

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

Прямых v1-требований (REQ-ID) у фазы нет — она инфраструктурная и разблокирует фазы 2–9. Ниже критерии приёмки фазы из ROADMAP.md, отображённые на результаты исследования:

| ID | Описание (критерий приёмки ROADMAP.md § Phase 1) | Research Support |
|----|--------------------------------------------------|------------------|
| SC-1 | ADR с явным выбором стека из вариантов A/B/C и обоснованием лежит в репозитории | Шаблон структуры `docs/adr/`; источник — CONTEXT.md D-01…D-08 (переноссятся в ADR) |
| SC-2 | Свежий клон поднимается одной командой: docker-compose запускает PostgreSQL и Redis, приложение отвечает на health-check | Паттерн compose: `depends_on.condition: service_healthy` + healthchecks (pg_isready / redis-cli ping / /healthz) [CITED: docs.docker.com]; паттерн /healthz (SELECT 1 + cache ping) |
| SC-3 | CI на каждый пуш: lint + typecheck + тесты; упавшая ступень краснит пайплайн | Workflow-паттерн: setup-python@v7 + cache pip + services postgres/redis [CITED: actions/setup-python, docs.github.com]; ступени = отдельные steps |
| SC-4 | Первая миграция воспроизводимо накатывается на чистую базу | Подход: без фейковых моделей — чистый том + `migrate` (contrib-миграции) + `showmigrations`; `makemigrations --check` в CI; pytest-django создаёт тест-БД через миграции на каждом пуше |
</phase_requirements>

## Project Constraints (from AGENTS.md)

- **Стек выбран пользователем явно** (уже сделано: Django/D-01) — агент не выбирает язык/фреймворк самостоятельно.
- **Нет прямых коммитов в `main`** — работа на ветках `feat/<name>`, `fix/<name>`, `chore/<name>` (правило `.opencode/rules/git-main-protection.md`).
- **Conventional Commits** для сообщений коммитов.
- **AGENTS.md обновляется тем же коммитом, что приносит тулинг/структуру** — фаза 1 приносит и то и другое ⇒ задача «update AGENTS.md» обязана войти в план (зафиксировать реальные команды: compose up, pytest, ruff, mypy).
- **New файлы сразу stage'ятся** (`git add`), коммит — только после явного подтверждения пользователем (правило `.opencode/rules/git-new-files.md`; в GSD-потоке коммитит оркестратор).
- Планировочные документы (`.planning/`) коммитятся (`commit_docs: true`).

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Health-check эндпоинт `/healthz` | API/Backend (Django app, `apps/core`) | Infrastructure (compose/GHA зондирует) | Проверка живости — ответственность приложения; инфраструктура только опрашивает |
| Runtime БД и кэша | Infrastructure (docker-compose сервисы) | — | PostgreSQL 18 и Redis 8 — контейнеры, управляются compose с healthchecks |
| WSGI-обслуживание | Infrastructure (gunicorn-контейнер) | API/Backend (приложение) | gunicorn — стандартный WSGI-сервер для Django в проде [CITED: deployment checklist «Switch away from manage.py runserver»] |
| CI-гейты (lint/typecheck/test) | CI (GitHub Actions) | Repo (конфиги ruff/mypy/pytest в pyproject.toml) | Качество проверяет пайплайн; пороги задаёт конфиг в репо |
| Миграции схемы | Data Layer (PostgreSQL, владелец — Django-приложения) | CI (воспроизводимость на тест-БД) | Миграции — нативный механизм Django (D-07); каждая миграция принадлежит app'у-владельцу таблиц |
| ADR выбора стека | Repo docs (`docs/adr/`) | — | Критерий №1 — артефакт в репозитории |
| Раздача статики | CDN/Static (WhiteNoise в контейнере) | — | WhiteNoise middleware обслуживает STATIC_ROOT без nginx на старте |

## Standard Stack

### Version verification

Все версии проверены живыми запросами к PyPI (`py -m pip index versions <pkg>`, 2026-11-18) и сквозным разрешением зависимостей: `py -m pip download -r <полный набор> --only-binary=:all: --python-version 3.13 --platform manylinux_2_17_x86_64` — **успешно, все wheel'ы существуют, конфликтов диапазонов нет** (транзитивно: asgiref 3.13.0, sqlparse 0.6.1, redis 8.1.0, tzdata 2026.6, typing_extensions 4.16.0, Faker 40.54.0, django-stubs-ext 6.1.2) [VERIFIED: PyPI registry].

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django | **5.2.19** (LTS-линия; последняя 5.2.x на сегодня) | Веб-фреймворк, ORM, admin, миграции | Выбор пользователя (D-01); LTS до апр. 2028 (STACK.md). Python: «5.2 \| 3.10, 3.11, 3.12, 3.13, 3.14 (added in 5.2.8)»; PostgreSQL: «Django supports PostgreSQL 14 and higher. psycopg 3.1.8+ or psycopg2 2.8.4+ is required, though the latest psycopg 3.1.8+ is recommended.» [CITED: docs.djangoproject.com/en/5.2/faq/install/, /ref/databases/] |
| djangorestframework | **3.18.3** | JSON API (точечно: поиск, мессенджер — D-03) | Требования: «Django (5.2, 6.0, 6.1); Python (3.10 … 3.15)» [CITED: django-rest-framework.org]; метаданные: `Requires-Dist: django>=5.2`, классифайеры Django 5.2/6.0/6.1 [VERIFIED: wheel METADATA] |
| psycopg\[binary\] | **3.3.9** | Драйвер PostgreSQL (psycopg 3) | Рекомендация Django 5.2 («the latest psycopg … is recommended»; «Support for psycopg2 is likely to be deprecated») [CITED: /ref/databases/]; cp313-manylinux wheel подтверждён пробой |
| gunicorn | **27.0.1** | WSGI-сервер (D-08) | Эталонный WSGI-сервер для Django; классифайеры Python 3.10–3.13 [VERIFIED: wheel METADATA] |
| django-redis | **7.0.0** | Кэш/сессии в Redis 8 | Требования README: «Python 3.10+, Django 5.2+, redis-py 4.0.2+, Redis server 2.8+» [CITED: github.com/jazzband/django-redis README]; `Requires-Dist: Django<7.0,>=5.2`, `redis>=4.0.2` → тянет redis-py 8.1.0 [VERIFIED: wheel METADATA] |
| whitenoise | **6.12.0** | Статика из контейнера без nginx | Классифайеры Django 4.2–6.0 [VERIFIED: wheel METADATA]; конфигурация middleware/storage — из официальных доков (см. Code Examples) |
| django-environ | **0.14.0** | 12-factor конфигурация из .env | Классифайеры Django 2.2–6.0, Python 3.10–3.14, `Requires-Python: >=3.9,<4` [VERIFIED: wheel METADATA] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | **9.2.0** | Тест-раннер | CI-ступень test (D-06) |
| pytest-django | **4.14.0** | Интеграция pytest ↔ Django (тест-БД, фикстуры) | Всегда; `Requires-Dist: pytest>=7.0.0`, классифайеры Django 5.2/6.0, Python 3.10–3.14 [VERIFIED: wheel METADATA] |
| ruff | **0.17.5** | Lint (+format по желанию) | CI-ступень lint (D-06) |
| mypy | **1.19.1** (НЕ 2.x) | Typecheck non-strict | CI-ступень typecheck (D-06). ВАЖНО: django-stubs 5.2.9 объявляет `compatible-mypy: mypy>=1.13,<1.20` [VERIFIED: wheel METADATA] — 2.x вне тестируемого диапазона |
| django-stubs | **5.2.9** | Типы для Django ORM/ settings | Всегда с mypy; мажор стабов трекает мажор Django (5.2.x ↔ Django 5.2), классифайеры Django 5.0–5.1–5.2 [VERIFIED: wheel METADATA] |
| coverage | **7.17.3** | Покрытие | Опционально в CI (`pytest --cov`) |
| factory_boy | **3.3.3** | Фабрики тестовых данных | Фундамент закладываем сейчас; первые фабрики — Phase 2 (User) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| psycopg 3 (psycopg\[binary\]) | psycopg2-binary | psycopg2 — легаси, Django openly deprecates; psycopg3 быстрее и рекомендован доками [CITED] |
| WhiteNoise | nginx-контейнер | nginx на скелете — лишний сервис и конфиг; WhiteNoise = 2 строки настроек. CDN/nginx — при реальном трафике (доки WhiteNoise прямо описывают апгрейд-путь) |
| mypy 1.19 | mypy 2.4.1 | 2.x резолвится без конфликта (extra — не hard requirement), но вне `compatible-mypy` django-stubs 5.2.9 — риск ошибок типечека на стабах; не стоит того |
| docker compose `services:` в CI | полный compose в CI | compose в CI требует build образа приложения (медленно) или `up` подмножества; `services:` нативен и быстрее. Решение: unit/integration тесты гоняются на раннере против `services:`, а «одна команда» (SC-2) проверяется локально/UAT через compose |
| django-environ | голый os.environ | os.environ чуть меньше зависимостей (и это документированный Django-паттерн: `SECRET_KEY = os.environ["SECRET_KEY"]` [CITED: deployment checklist]); django-environ даёт `env.db()/env.cache_url()` для URL-строк — удобнее при росте числа переменных |

**Installation** (пины скопированы из успешной пробы разрешения; в репо оформляются как `requirements/base.txt` и `requirements/dev.txt`):

```bash
# requirements/base.txt
Django==5.2.19
djangorestframework==3.18.3
gunicorn==27.0.1
psycopg[binary]==3.3.9
django-redis==7.0.0
whitenoise==6.12.0
django-environ==0.14.0

# requirements/dev.txt (-r base.txt +)
-r base.txt
pytest==9.2.0
pytest-django==4.14.0
ruff==0.17.5
mypy==1.19.1
django-stubs==5.2.9
coverage==7.17.3
factory_boy==3.3.3
```

## Package Legitimacy Audit

Гейт запущен: `gsd-tools query package-legitimacy check --ecosystem pypi <все 14 пакетов>`. **Все вердикты — `SUS`**, с причинами `unknown-downloads` / `too-new` — у PyPI-провайдера гейта нет телеметрии загрузок (`weeklyDownloads: null` у КАЖДОГО пакета, включая Django), а «too-new» считается по дате файла последнего релиза (свежий патч ≠ молодой проект). Это системные ложные срабатывания, а не сигнал о slopsquatting. Компенсирующая проверка выполнена: **canonические исходные репозитории извлечены из подписанных мейнтейнером wheel-METADATA** (скачаны с PyPI в этой сессии):

| Package | Registry | Возраст проекта | Downloads (гейт) | Source Repo (из wheel METADATA) | Verdict (гейт) | Disposition |
|---------|----------|-----------------|------------------|----------------------------------|----------------|-------------|
| Django | PyPI | 20+ лет (с 1.0 в 2005) | null | github.com/django/django | SUS (ложное) | Approved |
| djangorestframework | PyPI | 14+ лет | null | github.com/encode/django-rest-framework | SUS (ложное) | Approved |
| gunicorn | PyPI | 15+ лет | null | github.com/benoitc/gunicorn | SUS (ложное) | Approved |
| psycopg | PyPI | 24+ лет (проект) | null | psycopg.org | SUS (ложное) | Approved |
| django-redis | PyPI | 13+ лет | null | github.com/jazzband/django-redis | SUS (ложное) | Approved |
| whitenoise | PyPI | 12+ лет | null | github.com/evansd/whitenoise | SUS (ложное) | Approved |
| django-environ | PyPI | 12+ лет | null | github.com/joke2k/django-environ | SUS (ложное) | Approved |
| pytest | PyPI | 20+ лет | null | github.com/pytest-dev/pytest | SUS (ложное) | Approved |
| pytest-django | PyPI | 15+ лет | null | github.com/pytest-dev/pytest-django | SUS (ложное) | Approved |
| ruff | PyPI | 4+ года | null | github.com/astral-sh/ruff | SUS (ложное) | Approved |
| mypy | PyPI | 13+ лет | null | github.com/python/mypy | SUS (ложное) | Approved |
| django-stubs | PyPI | 6+ лет | null | github.com/typeddjango/django-stubs | SUS (ложное) | Approved |
| coverage | PyPI | 18+ лет | null | github.com/coveragepy/coveragepy | SUS (ложное) | Approved |
| factory_boy | PyPI | 13+ лет | null | github.com/FactoryBoy/factory_boy | SUS (ложное) | Approved |

**Packages removed due to \[SLOP\] verdict:** none.
**Packages flagged as suspicious \[SUS\]:** формально все (см. выше); реально подозреваемых нет — имена Django/DRF/PostgreSQL приходят из locked-решения пользователя, остальные подтверждены wheel-METADATA и официальными доками, версии запинены точно (`==`) и разрешены пробой. Дополнительный контр-шкип-чек: none — PyPI не исполняет postinstall-скрипты (модель дистрибуции отличается от npm; sed-протокол неприменим).

## Architecture Patterns

### System Architecture Diagram

```
 [Разработчик / CI-триггер]          [git push]
        │                                   │
        ▼                                   ▼
 ┌──────────────────────┐        ┌─────────────────────────────┐
 │  docker compose up   │        │  GitHub Actions (CI)        │
 │  (одна команда, SC-2)│        │  on: push / pull_request    │
 └──────────┬───────────┘        └──────────────┬──────────────┘
            │ создаёт сеть                       │
            ▼                                    ▼
 ┌──────────────────────────────────┐  ┌───────────────────────────────┐
 │ compose-сеть                     │  │ ubuntu-runner                 │
 │                                  │  │  1) ruff check      (lint)    │
 │  ┌────────────┐ healthcheck:     │  │  2) mypy            (types)   │
 │  │ db         │ pg_isready       │  │  3) pytest --cov    (tests)   │
 │  │ postgres:18│◄──────┐          │  │        │                      │
 │  └─────┬──────┘       │          │  └────────┼──────────────────────┘
 │        │ service_healthy         │           │ SQL/redis на localhost
 │        ▼              │          │           ▼
 │  ┌────────────┐       │          │  ┌────────────────────┐
 │  │ cache      │ healthcheck:     │  │ services:          │
 │  │ redis:8    │ redis-cli ping   │  │  postgres:18       │
 │  └─────┬──────┘       │          │  │  redis:8           │
 │        │ service_healthy         │  │  (health-cmd       │
 │        ▼              │          │  │   pg_isready)      │
 │  ┌────────────────────┴───┐      │  └────────────────────┘
 │  │ web (build Dockerfile) │      │
 │  │ python:3.13-slim       │      │
 │  │ entrypoint: migrate →  │      │
 │  │  collectstatic →       │      │
 │  │  gunicorn config.wsgi  │      │
 │  │  GET /healthz →        │      │
 │  │   SELECT 1 + cache ping│      │
 │  └────────────────────────┘      │
 └──────────────────────────────────┘
  (volume pgdata персистит схему между рестартами)
```

Путь основного сценария: `docker compose up` → db/cache проходят healthchecks → web стартует (entrypoint накатывает миграции) → внешний запрос `GET /healthz` → 200 `{"status": "ok"}`. В CI тот же код проверяется ступенями ruff/mypy/pytest; pytest через pytest-django создаёт тест-БД (миграции выполняются) — SC-3 и SC-4 автоматически проверяются каждым пушем.

### Recommended Project Structure

```
AI-pet-project/
├── AGENTS.md                  # ОБНОВЛЯЕТСЯ тем же коммитом (команды тулинга)
├── README.md                  # как поднять одной командой
├── .gitignore                 # .env, __pycache__, staticfiles/, .venv/
├── .gitattributes             # * text=auto eol=lf  (защита entrypoint от CRLF)
├── .env.example               # все переменные с безопасными дефолтами dev
├── .dockerignore
├── Dockerfile                 # python:3.13-slim + requirements + код
├── entrypoint.sh              # migrate → collectstatic → exec gunicorn
├── compose.yaml               # db / cache / web (+ healthchecks, volumes)
├── requirements/
│   ├── base.txt               # рантайм (пины ==)
│   └── dev.txt                # -r base.txt + тесты/линтеры
├── pyproject.toml             # [tool.ruff] [tool.mypy] [tool.pytest] (+ django-stubs)
├── docs/
│   ├── PRD.md                 # (уже существует)
│   └── adr/
│       └── 0001-choice-of-stack.md   # SC-1: ADR с решением B и обоснованием
├── config/                    # Django-проект (не приложение)
│   ├── settings/
│   │   ├── base.py            # общее; env через django-environ; INSTALLED_APPS с apps.*
│   │   ├── dev.py             # DEBUG=True, ALLOWED_HOSTS=[]
│   │   ├── prod.py            # DEBUG=False, SECURITY-настройки
│   │   └── test.py            # для CI/pytest: быстрые хэшеры и т.п.
│   ├── urls.py                # path("healthz/", ...), path("admin/", ...)
│   └── wsgi.py                # gunicorn config.wsgi:application
├── apps/
│   ├── core/                  # /healthz, общая инфраструктура (без доменных таблиц)
│   ├── accounts/              # пустой stub (модели — Phase 2, custom User)
│   ├── catalog/               # stub (Phase 3)
│   ├── geo/                   # stub (Phase 3)
│   ├── listings/              # stub (Phase 4)
│   ├── search/                # stub (Phase 7)
│   ├── messaging/             # stub (Phase 8)
│   └── moderation/            # stub (Phase 9)
├── templates/                 # базовые шаблоны SSR (D-03)
├── static/                    # исходники статики (CSS/логотип)
└── tests/
    ├── conftest.py
    └── test_health.py         # SC-2 smoke: /healthz 200 при живых db+cache
```

### Pattern 1: Split settings (base/dev/prod/test)

**What:** Один пакет `config.settings` с модулем на окружение; выбор через `DJANGO_SETTINGS_MODULE`.
**When to use:** Всегда в 12-factor-проекте. Deployment checklist Django явно разделяет dev/prod значения (SECRET_KEY, DEBUG, ALLOWED_HOSTS, CACHES, DATABASES) и рекомендует «publish suitable settings for development, and … a private settings module for production» [CITED: docs.djangoproject.com/en/5.2/howto/deployment/checklist/].
**Пример:**

```python
# config/settings/base.py — секреты только из env (Source: Django deployment checklist)
import environ

env = environ.Env()
DATABASES = {"default": env.db("DATABASE_URL")}          # [ASSUMED] API django-environ
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",      # verbatim из README django-redis
        "LOCATION": env("REDIS_URL", default="redis://cache:6379/0"),
    }
}
SECRET_KEY = env("DJANGO_SECRET_KEY")                     # «consider loading it from an environment variable» [CITED]
```

### Pattern 2: Health-check без раскрытия внутренностей

**What:** Синхронный view `/healthz`: SELECT 1 через `django.db.connection` + `cache.set/get` через django-redis; ответ — только `{"status": "ok"}` (200) или 503; никаких версий, хостов, стектрейсов.
**When to use:** Скелет (SC-2), compose-healthcheck web-контейнера, будущие LB-пробы.
**Example:** см. Code Examples → «Health endpoint».

### Pattern 3: Границы модулей = границы таблиц (модульный монолит Django)

**What:** Каждый app из D-04 владеет своими таблицами; чужие таблицы не читаются напрямую. На практике в Django это дисциплина импортов: `messaging` не делает `from apps.listings.models import Listing`, а получает данные через сервис-функцию/менеджер модуля-владельца (`apps.listings.services.get_listing_snapshot(...)`); FK между таблицами разных модулей допустим (`ON DELETE SET NULL` план Phase 4/8 — из ARCHITECTURE.md).
**When to use:** Немедленно — границы дешёвые, пока apps пустые; дорожают с каждой чужой таблицей.
**Как удерживать:** ревью-правило + (опционально, на усмотрение) import-linter в будущем.

### Pattern 4: «Первая миграция» без фейковой схемы

**What:** Никаких искусственных healthcheck-таблиц. Первый `migrate` на чистой базе накатывает встроенные миграции contrib-приложений (auth, admin, contenttypes, sessions) — этого достаточно, чтобы доказать работоспособность механизма миграций (SC-4). Первая доменная миграция появится в Phase 2 (`accounts.0001` — custom User). В CI добавляется `python manage.py makemigrations --check --dry-run` — падение = рассинхрон моделей и миграций [ASSUMED — стандартные команды django-admin].
**When to use:** Greenfield-скелет.

### Pattern 5: Compose-оркестрация готовности сервисов

**What:** `depends_on` с `condition: service_healthy` + healthchecks у db/cache; entrypoint web сам накатывает миграции (идемпотентно) и стартует gunicorn.
**When to use:** SC-2 «одна команда». Доки Compose: «The solution for detecting the ready state of a service is to use the `condition` attribute … `service_healthy`. This specifies that a dependency is expected to be "healthy", which is defined with `healthcheck`, before starting a dependent service.» [CITED: docs.docker.com/compose/how-tos/startup-order/]

### Anti-Patterns to Avoid

- **psycopg2 в новом проекте** — Django 5.2 рекомендует psycopg 3 и готовит deprecation psycopg2 [CITED: /ref/databases/].
- **Alpine-образ для web** — psycopg-binary поставляется manylinux (glibc) wheel'ами (таги колёс из пробы: `manylinux2014_x86_64`); на musl бинарные wheel'ы не работают [ASSUMED — рассуждение по тагам wheel]. `*-alpine` — только для db/cache контейнеров; web = `python:3.13-slim`.
- **Жёсткий `depends_on` без condition** — Compose ждёт лишь «running», не «ready»: «Compose does not wait until a container is "ready", only until it's running» [CITED: docs.docker.com].
- **Sleep-петли в entrypoint вместо healthchecks** — то, что healthchecks решают декларативно.
- **Обращение между apps через чужие ORM-модели** — ломает границы модульного монолита (см. Pattern 3).
- **SECRET_KEY/пароли в settings-файлах или git** — «avoid committing it to source control» [CITED: deployment checklist].

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Парсинг .env/URL-строк БД | Свой os.environ-обвяз | django-environ (или голый os.environ для минимализма) | Экранирование, дефолты, `env.db()` парсит postgres:// URL; минимум поверхности для ошибок |
| Раздача статики в контейнере | Свой view/роут статfiles | WhiteNoise middleware | Кэш-заголовки, компрессия, manifest-хэши — самописное повторение целой библиотеки |
| WSGI-обслуживание | http.server / runserver в проде | gunicorn | runserver не для прода [CITED: deployment checklist «Switch away from manage.py runserver»] |
| Управление тест-БД | Свой create/drop в фикстурах | pytest-django | Тест-БД создаётся из миграций автоматически; `--reuse-db`, `django_db` marker |
| Типы для Django ORM | Игнорирование mypy на моделях | django-stubs 5.2.9 + плагин | Тысячи строк стабов; самописные = вечный долг |
| Healthcheck-протокол compose | bash-петли `until pg_isready` | `condition: service_healthy` | Декларативно, документировано [CITED: docs.docker.com] |
| Кэш-клиент Redis | Прямой redis-py в настройках Django | django-redis backend | Интеграция с Django cache framework (сессии, `cache.get/set` API) |

**Key insight:** всё перечисленное — «deceptively simple» обвязки, где 80% кода — edge cases (таймауты, реконнекты, кодировки, конкурентный доступ); каждая имеет каноническую библиотеку с 10+ годами продакшена.

## Runtime State Inventory

> Greenfield-фаза — исходного кода, данных и сервисов нет. Категория неприменима; section omitted by template rule.

## Common Pitfalls

### Pitfall 1: Custom User после первой миграции (ловушка AUTH_USER_MODEL)
**What goes wrong:** Phase 1 прогоняет `migrate` с дефолтным `auth.User`; Phase 2 вводит кастомную User-модель — на уже инициализированной базе это refactor-миграция повышенного риска.
**Why it happens:** Django требует `AUTH_USER_MODEL` до первого `migrate` для безболезненной смены.
**How to avoid:** База фазы 1 — одноразовая (dev-том): допустимо прогнать migrate со стандартным auth. В плане Phase 2 явно заложить: кастомный User вводится ДО появления пользовательских данных + пересоздание dev-тома (`docker compose down -v`). Зафиксировать это в ADR фазы 1 (решение осознанное).
**Warning signs:** попытка `migrate` после смены AUTH_USER_MODEL на непустой базе.

### Pitfall 2: mypy 2.x с django-stubs 5.2.9
**What goes wrong:** mypy 2.4.1 резолвится pip'ом без конфликтов (compatible-mypy — это extra), но падает/ложит ошибки на стабах.
**Why it happens:** django-stubs 5.2.9 объявляет протестированный диапазон `mypy>=1.13,<1.20` [VERIFIED: wheel METADATA].
**How to avoid:** пинить `mypy==1.19.1` (в диапазоне; cp313 wheel проверен).
**Warning signs:** каскад нерелевантных ошибок типов в `django-stubs/*` на CI.

### Pitfall 3: `$$` в compose healthcheck
**What goes wrong:** `pg_isready -U ${POSTGRES_USER}` — compose подставляет свои переменные (или пустоту), healthcheck всегда unhealthy.
**Why it happens:** `${}` интерполируется compose; для передачи в контейнер нужно `$$`.
**How to avoid:** как в официальном примере: `test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]` [CITED: docs.docker.com — verbatim].
**Warning signs:** web вечно ждёт `service_healthy` у db.

### Pitfall 4: ALLOWED_HOSTS ≠ хост пробы
**What goes wrong:** `DEBUG=False` + запрос healthz по имени сервиса/IP → 400, хотя приложение живо.
**Why it happens:** «When `DEBUG = False`, Django doesn't work at all without a suitable value for `ALLOWED_HOSTS`» [CITED: deployment checklist].
**How to avoid:** в dev/prod-настройках задать ALLOWED_HOSTS из env (включая `localhost`, `web`, `127.0.0.1`).
**Warning signs:** curl /healthz даёт 400 Bad Request.

### Pitfall 5: CRLF в entrypoint.sh (Windows-хост!)
**What goes wrong:** файл, закоммиченный из Windows с CRLF, в linux-контейнере падает `/bin/sh^M: not found`.
**Why it happens:** git на Windows конвертирует концы строк.
**How to avoid:** `.gitattributes` со строкой `* text=auto eol=lf` (минимум для `*.sh`) — заложить в скелет с первого коммита.
**Warning signs:** web-контейнер умирает на старте с `^M` в логе.

### Pitfall 6: WhiteNoise: порядок middleware и отсутствие collectstatic
**What goes wrong:** 404 на статике в прод-контейнере.
**Why it happens:** middleware не на месте («The WhiteNoise middleware should be placed directly after the Django SecurityMiddleware … and before all other middleware») либо не выполнен collectstatic [CITED: whitenoise.evans.io/en/stable/django.html].
**How to avoid:** entrypoint выполняет `collectstatic --noinput` перед gunicorn; STORAGES-бэкенд `whitenoise.storage.CompressedManifestStaticFilesStorage` (verbatim из доков).
**Warning signs:** `ValueError: Missing staticfiles manifest entry` — забыт collectstatic.

### Pitfall 7: Тесты тормозят из-за WhiteNoise
**What:** прогон pytest замедляется сканированием статики.
**Why:** WhiteNoise делает работу на старте процесса.
**How to avoid:** в `config/settings/test.py` задать `WHITENOISE_AUTOREFRESH = True` — «The simplest way to fix this is to make sure that during testing the `WHITENOISE_AUTOREFRESH` setting is set to `True`» [CITED: whitenoise docs — verbatim].

### Pitfall 8: Хост без `python` в PATH
**What goes wrong:** локальные команды `python manage.py …` не работают на этой Windows-машине.
**Why it happens:** на хосте только лаунчер `py` (Python 3.14.7); `python`/`pip` не в PATH (проверено этой сессией).
**How to avoid:** весь workflow фазы — через `docker compose` (`docker compose run --rm web python manage.py …`); задокументировать в README/AGENTS.md. Запуск на хосте 3.14 вдобавок ограничен: gunicorn 27 и django-stubs 5.2.9 заявляют максимум 3.13 [VERIFIED: wheel METADATA].
**Warning signs:** «'python' is not recognized…».

### Pitfall 9: порядок пайпа CI: миграции дрейфуют молча
**What goes wrong:** модели правятся, миграции не создаются; прод-деплой падает.
**How to avoid:** ступень `python manage.py makemigrations --check --dry-run` в CI до pytest [ASSUMED — стандартная команда].

## Code Examples

### Health endpoint (apps/core/views.py)

```python
# Паттерн — рекомендация исследования ([ASSUMED] по форме; API — официальные django.db/django.core.cache)
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def healthz(request):
    checks = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["db"] = "ok"
        cache.set("healthz:ping", "1", timeout=5)
        checks["cache"] = "ok"
    except Exception:
        return JsonResponse({"status": "fail", "checks": checks}, status=503)
    return JsonResponse({"status": "ok", "checks": checks})
```

Никаких внутренностей (версии/хосты/стек) в ответе; 503 при недоступности любой зависимости.

### compose.yaml (ключевые фрагменты; healthcheck db — verbatim из доков Docker)

```yaml
# Source: docs.docker.com/compose/how-tos/startup-order/ (пример официально использует postgres:18)
services:
  db:
    image: postgres:18-alpine            # [ASSUMED] суффикс -alpine; сам тег postgres:18 — из примера доков
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-classifieds}
      POSTGRES_USER: ${POSTGRES_USER:-classifieds}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set in .env}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"           # только localhost на хосте разработчика
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]   # verbatim
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 10s

  cache:
    image: redis:8-alpine                # [ASSUMED] тег; Redis 8 — D-05
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"] # [ASSUMED] общепринятая команда
      interval: 10s
      retries: 5

  web:
    build: .
    env_file: .env
    command: ["./entrypoint.sh"]         # migrate → collectstatic → exec gunicorn
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy       # verbatim-паттерн доков
        restart: true                    # verbatim-паттерн доков
      cache:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/healthz')\""]  # [ASSUMED] curl отсутствует в slim
      interval: 15s
      retries: 5
      start_period: 20s

volumes:
  pgdata:
```

### Dockerfile + entrypoint

```dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTEcode=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/base.txt
COPY . .
RUN chmod +x entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
```

```bash
#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

### CACHES + сессии (verbatim из README django-redis)

```python
# Source: github.com/jazzband/django-redis README («Configure as cache backend»)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",   # у нас: redis://cache:6379/0 из env
    }
}
# Опционально (Phase 2+, когда появятся сессии):
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"
```

### WhiteNoise (verbatim из официальных доков)

```python
# Source: whitenoise.evans.io/en/stable/django.html
MIDDLEWARE = [
    # ...
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ...
]
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
# dev: "whitenoise.runserver_nostatic" в начало INSTALLED_APPS (там же, verbatim)
```

### pyproject.toml (тест-конфиг — verbatim формат pytest 9+; остальное — [ASSUMED])

```toml
[tool.pytest]
DJANGO_SETTINGS_MODULE = "config.settings.test"   # verbatim-формат: pytest-django docs,
                                                  # «For pytest 9.0 and later, use the native TOML format: [tool.pytest]»

[tool.ruff]
target-version = "py313"

[tool.mypy]
python_version = "3.13"
plugins = ["mypy_django_plugin.main"]             # [ASSUMED]
ignore_missing_imports = true                     # non-strict старт (D-06)

[tool.django-stubs]
django_settings_module = "config.settings.test"   # [ASSUMED]
```

### GitHub Actions CI

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
permissions:
  contents: read        # verbatim: actions/setup-python README («Recommended permissions»)
jobs:
  check:
    runs-on: ubuntu-latest
    services:
      postgres:                                   # verbatim-структура: docs.github.com
        image: postgres:18                        # «creating-postgresql-service-containers»
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:                                      # [ASSUMED] по аналогии с postgres-блоком
        image: redis:8-alpine
        ports:
          - 6379:6379
    env:
      DATABASE_URL: postgres://postgres:postgres@localhost:5432/classifieds
      REDIS_URL: redis://localhost:6379/0
      DJANGO_SECRET_KEY: ci-secret-key-not-used
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: '3.13'                  # verbatim-формат из README
          cache: 'pip'                            # verbatim: «caching pip dependencies»
          cache-dependency-path: requirements/*.txt
      - run: pip install -r requirements/dev.txt
      - name: Lint                                # ступень 1 (D-06)
        run: ruff check .
      - name: Typecheck                           # ступень 2
        run: mypy .
      - name: Migrations drift check              # [ASSUMED] команда
        run: python manage.py makemigrations --check --dry-run
      - name: Tests                               # ступень 3
        run: coverage run -m pytest -v && coverage report
```

Каждая ступень — отдельный step: падение любой краснит job (критерий №3). Примечание из README setup-python: для попадания в кэш пинить версии в requirements (у нас `==`) — «To be sure that the cache will be used, please stick to a specific dependency version» [CITED].

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| psycopg2 | psycopg 3 (psycopg\[binary\]) | Django рекомендует psycopg 3 c 4.2; в 5.2 — «likely to be deprecated» psycopg2 [CITED] | Ставим psycopg 3 сразу |
| `settings.py` монолит | split settings + env (12-factor) | давно мейнстрим; закреплено deployment checklist | `config/settings/{base,dev,prod,test}` |
| flake8+isort+black россыпью | ruff (lint+format, один инструмент) | ruff — стандарт de facto к 2026 | Одна ступень lint, один конфиг |
| `[tool.pytest.ini_options]` | `[tool.pytest]` native TOML | pytest 9.0 | Мы на pytest 9.2 ⇒ native-формат [CITED: pytest-django docs] |
| docker-compose v1 (отдельный бинарь) | Compose v2 (`docker compose`) | 2023 | Команда `docker compose up` (на хосте v2.40.2 ✓) |
| healthcheck через sleep/wait-for-it | `depends_on.condition: service_healthy` | Compose spec давно | Декларативно [CITED: docs.docker.com] |

**Deprecated/outdated:**
- psycopg2: «Support for `psycopg2` is likely to be deprecated and removed at some point in the future» [CITED: Django 5.2 ref/databases].
- `manage.py runserver` как прод-сервер: «not designed for a production setting» [CITED: deployment checklist].
- Django 6.x существует (6.1.3 latest [VERIFIED: PyPI]), но D-01 фиксирует 5.2 LTS — обновление отдельным решением после LTS-цикла.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Форма healthz-view (SELECT 1 + cache ping, JSON без внутренностей) — рекомендация исследования, не цитата | Code Examples | Низкий: паттерн тривиален; при желании заменить на django-health-check пакет (не рекомендую: лишняя зависимость) |
| A2 | `redis-cli ping` как healthcheck cache-контейнера | Code Examples | Низкий: общепринятая команда; альтернатива `redis-cli -h localhost ping` |
| A3 | Web-healthcheck через python urllib one-liner (в slim нет curl/wget) | Code Examples | Низкий: альтернатива — поставить curl в образ (+мб к образу) |
| A4 | `docker compose up --wait` для скрипта проверки SC-2 | Validation | Низкий: fallback — polling curl в цикле |
| A5 | Блоки конфигурации ruff/mypy/django-stubs в pyproject (target py313, plugins, non-strict) | Code Examples | Низкий: детали конфига — discretion фазы |
| A6 | API django-environ (`env.db()`, `env("REDIS_URL")`) | Code Examples | Низкий: fallback — голый `os.environ` (это документированный Django-паттерн [CITED]) |
| A7 | Теги образов `python:3.13-slim`, `postgres:18-alpine`, `redis:8-alpine` существуют на Docker Hub | Code Examples | Низкий: `postgres:18` подтверждён примером доков Docker; суффиксы — конвенция тегов официальных образов; executor проверит pull'ом |
| A8 | psycopg-binary несовместим с musl (alpine) → web-образ только glibc slim | Anti-Patterns | Средний при нарушении: падение установки в образе; проверяется первым build'ом |
| A9 | `makemigrations --check --dry-run` / `showmigrations` — команды django-admin | Patterns, Validation | Низкий: базовые команды Django |
| A10 | GHA-блок `services: redis:` (postgres-блок — CITED, redis — по аналогии) | Code Examples | Низкий |
| A11 | GitHub Free даёт достаточно CI-минут для private-репо | Open Questions | Низкий: 2000 мин/мес на Free-плане; наш пайплайн ~2–4 мин |
| A12 | entrypoint-подход `migrate → collectstatic → gunicorn` в dev-контейнере приемлем для скелета | Code Examples | Низкий: прод-разворачивание вне scope фазы 1 |
| A13 | Дата: «postgres:18-alpine» актуален как тег (проверен только `postgres:18`) | Code Examples | Низкий: при отсутствии тега — убрать суффикс |

**Если таблица пуста — все утверждения верифицированы.** Здесь 13 осознанных [ASSUMED] — все низко-рисковые, проверяются первым `docker compose build/up`.

## Open Questions

1. **Кастомный User и первая миграция (Pitfall 1)**
   - Что знаем: Phase 2 вводит accounts с кастомной User; Phase 1 уже прогоняет миграции.
   - Что неясно: хочет ли пользователь stub `accounts.0001_custom_user` уже в фазе 1 (тогда Phase 2 проще) или принять сброс dev-тома.
   - Рекомендация: не тянуть Phase 2 в Phase 1; зафиксировать в ADR «dev-БД одноразовая до Phase 2». Если пользователь предпочтёт сразу — план легко расширяется.
2. **CI-минуты GitHub для private-репо**
   - Что знаем: workflow ~2–4 мин/пуш; Free-план даёт 2000 мин/мес [ASSUMED].
   - Рекомендация: подтвердить план аккаунта при первом красном/ограничении; public-репо снял бы вопрос, но проект приватный по природе.
3. **Разделять ли lint/typecheck/test на отдельные jobs (matrix)**
   - Что знаем: один job с тремя steps уже выполняет критерий №3; отдельные jobs параллельнее, но каждый заново ставит зависимости (медленнее при кэш-промахах).
   - Рекомендация: для скелета — один job; разбить позже при росте сьюта.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker + Compose v2 | SC-2 (одна команда), сборка образа | ✓ | Docker 28.5.1 / Compose v2.40.2-desktop | — |
| Git | ветки/коммиты | ✓ | 2.56.0.windows.1 | — |
| Python на хосте | локальный запуск тестов вне Docker | △ (только `py` 3.14.7; `python`/`pip` не в PATH) | 3.14.7 через лаунчер | Весь workflow через `docker compose` (рекомендуется); host-3.14 вдобавок вне классифайеров gunicorn/django-stubs |
| Node.js | GSD-тулинг (не для стека) | ✓ | 24.21.0 | — |
| GitHub Actions runners | SC-3 (CI) | внешний сервис | — | недоступен локально; первый прогон CI проверить push'ем (manual UAT) |

**Missing dependencies with no fallback:** нет.
**Missing dependencies with fallback:** host-Python (замещён docker-first workflow).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.2.0 + pytest-django 4.14.0 (+ coverage 7.17.3) |
| Config file | `pyproject.toml` — секция `[tool.pytest]` c `DJANGO_SETTINGS_MODULE = "config.settings.test"` (native TOML для pytest 9+; формат verbatim из доков pytest-django) — создаётся фазой (Wave 0) |
| Quick run command | `docker compose run --rm web pytest -x -q` (или `docker compose exec web pytest -x -q` при поднятом стеке) |
| Full suite command | `docker compose run --rm web coverage run -m pytest -v && docker compose run --rm web coverage report` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SC-1 | ADR лежит в репозитории с выбором B и обоснованием | artifact check (grep) | `git ls-files docs/adr` + просмотр | ❌ Wave 0 (создаётся фазой) |
| SC-2 | compose поднимает db+cache+web; /healthz отвечает 200 | smoke (требует docker) | `docker compose down -v && docker compose up -d --wait && curl -fsS http://localhost:8000/healthz` [ASSUMED: флаг --wait] | ❌ Wave 0: `scripts/verify_bootstrap.(sh|cmd)` |
| SC-2 (unit-уровень) | /healthz возвращает 200 при живых зависимостях | integration (db+cache) | `docker compose run --rm web pytest tests/test_health.py -x` | ❌ Wave 0: `tests/test_health.py` |
| SC-3 | CI: ruff/mypy/pytest краснят пайплайн | manual-only (внешний сервис) — файл workflow проверяется ревью; фактический прогон = push | `git ls-files .github/workflows` + ревью YAML | ❌ Wave 0: `.github/workflows/ci.yml` |
| SC-4 | Миграция воспроизводимо накатывается на чистую базу | integration + CI-ступень | `docker compose down -v && docker compose up -d --wait db && docker compose run --rm web python manage.py migrate && docker compose run --rm web python manage.py showmigrations` (все `[X]`); в CI: `python manage.py makemigrations --check --dry-run` + pytest-django создаёт тест-БД из миграций | ❌ Wave 0 (входит в scripts/verify_bootstrap и CI) |

### Sampling Rate
- **Per task commit:** `docker compose run --rm web pytest -x -q` (быстрая выборка; <30 c после прогрева образов)
- **Per wave merge:** полный сьют с coverage (`coverage run -m pytest && coverage report`)
- **Phase gate (`/gsd-verify-work`):** полный сьют зелёный + ручной прогон `scripts/verify_bootstrap` (SC-2/SC-4 end-to-end) + просмотр зелёного прогона CI на GitHub (SC-3)

### Wave 0 Gaps
- [ ] `tests/__init__.py`, `tests/conftest.py` — фикстуры (client, db)
- [ ] `tests/test_health.py` — покрывает SC-2 unit-уровень
- [ ] `config/settings/test.py` — быстрые хэшеры, `WHITENOISE_AUTOREFRESH=True`, env-дефолты CI
- [ ] `pyproject.toml` — `[tool.pytest]` секция (DJANGO_SETTINGS_MODULE)
- [ ] `.github/workflows/ci.yml` — workflow с services
- [ ] `scripts/verify_bootstrap.sh` (+`.cmd` для Windows-хоста) — скрипт приёмки SC-2/SC-4
- [ ] Инструменты уже входят в `requirements/dev.txt` (pytest/pytest-django/coverage) — отдельной установки не требуется

## Security Domain

> security_enforcement: true, ASVS level 1 (config.json). Фаза инфраструктурная — поверхности атаки минимальны, но закладываются сейчас.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no (фаза 1) | Пользовательской аутентификации нет; Django Admin включён с дефолтными механизмами (login-форм, CSRF) — наружу не публикуется |
| V3 Session Management | частично | contrib sessions (БД); Redis-сессии — Phase 2+ (README django-redis: `SESSION_ENGINE = "django.contrib.sessions.backends.cache"`) |
| V4 Access Control | no (фаза 1) | Появляется с фазами домена |
| V5 Input Validation | минимально | `/healthz` не принимает входных данных (GET без параметров); доменная валидация — Django forms/DRF serializers (фазы 2+) |
| V6 Cryptography | частично | `SECRET_KEY` только из env [CITED: deployment checklist]; парольное хэширование — встроенное в Django (PBKDF2) |
| V14 Configuration | yes | `DEBUG=False` в prod («You must never enable debug in production» [CITED]); `ALLOWED_HOSTS` из env; `manage.py check --deploy` в CI/чеклисте приёмки |

### Known Threat Patterns for Django skeleton + Docker

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Раскрытие внутренностей через health-check | Information Disclosure | Ответ только `{"status": "ok"}` / 503 — без версий, DSN, стектрейсов |
| Утечка секретов в git | Information Disclosure | `.env` в `.gitignore`; `.env.example` без секретов; значения по умолчанию только dev; `${POSTGRES_PASSWORD:?}` — compose падает без значения |
| Debug-страницы в проде | Information Disclosure | prod-настройки `DEBUG=False`; deployment checklist verbatim |
| Подделка Host | Spoofing/Tampering | `ALLOWED_HOSTS` явный список [CITED] |
| Доступ к БД/кэшу извне | Elevation | Порты db/cache публиковать только на `127.0.0.1` хоста; внутри compose-сети — по именам сервисов |
| Supply chain (PyPI) | Tampering | Точные пины `==` (проверены пробой); обновление — осознанным коммитом; легитимность — см. Package Legitimacy Audit |
| CSRF на админке | Tampering | Встроенные Django-механизмы (CsrfViewMiddleware в base.py); админка не экспонируется в internet на фазе 1 |

## Sources

### Primary (HIGH confidence)
- pip index / pip download (живой PyPI, 2026-11-18): версии Django 5.2.19/6.1.3, DRF 3.18.3, gunicorn 27.0.1, psycopg(-binary) 3.3.9, django-redis 7.0.0, whitenoise 6.12.0, django-environ 0.14.0, pytest 9.2.0, pytest-django 4.14.0, ruff 0.17.5, mypy 2.4.1/1.19.1, django-stubs 5.2.9/6.1.2, coverage 7.17.3, factory_boy 3.3.3, redis 8.1.0; сквозная проба разрешения для py3.13/manylinux успешна; wheel-METADATA (Requires-Dist/classifiers/Project-URL) извлечены для ключевых пакетов
- docs.djangoproject.com/en/5.2/faq/install/ — матрица Python↔Django (таблица verbatim)
- docs.djangoproject.com/en/5.2/ref/databases/ — «PostgreSQL 14 and higher», psycopg 3.1.8+, deprecation psycopg2, connection pool (`OPTIONS.pool`), server-side binding
- docs.djangoproject.com/en/5.2/howto/deployment/checklist/ — SECRET_KEY/DEBUG/ALLOWED_HOSTS/check --deploy
- django-rest-framework.org — Requirements: «Django (5.2, 6.0, 6.1); Python (3.10 … 3.15)»
- github.com/jazzband/django-redis README — Requirements, CACHES verbatim, SESSION_ENGINE, hiredis-опция
- whitenoise.evans.io/en/stable/django.html — middleware-порядок, STORAGES, runserver_nostatic, WHITENOISE_AUTOREFRESH для тестов, «not suitable for … media files»
- docs.docker.com/compose/how-tos/startup-order/ — condition: service_healthy; пример с postgres:18 + pg_isready healthcheck (verbatim, включая `$$`)
- docs.github.com/en/actions/using-containerized-services/creating-postgresql-service-containers — services-блок с --health-cmd pg_isready (verbatim)
- github.com/actions/setup-python README (main/v7) — python-version '3.13', cache: 'pip', permissions: contents: read, замечание о пинах для кэша
- pytest-django.readthedocs.io/en/latest/ — [tool.pytest] native TOML для pytest 9+, DJANGO_SETTINGS_MODULE, --no-migrations/--reuse-db, фикстуры (client, admin_user, settings, mailoutbox)

### Secondary (MEDIUM confidence)
- `.planning/research/STACK.md` (2026-11-18, HIGH по версиям на тот момент) — обоснование варианта B, PG FTS/Redis роли; сверено: строки версий не разошлись с сегодняшней пробой
- `.planning/research/ARCHITECTURE.md` — границы модулей, сервис-контракты, ON DELETE SET NULL-план

### Tertiary (LOW confidence)
- Встроенный WebSearch — HTTP 403 в окружении (как и в сессии stack-research); investigation выполнена прямыми WebFetch к первоисточникам выше
- gsd-tools seam `research-plan` — не читает валидный input-файл в этом окружении (4 попытки: abs/rel пути, temp/repo ФС); workaround: прямые fetch'ы, т.к. все MCP-провайдеры отключены в config.json и routing свёлся бы к webfetch/websearch

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — версии и совместимость подтверждены живой пробой разрешения pip + wheel-METADATA + официальными доками с verbatim-цитатами; единственный discovered-риск (mypy↔django-stubs) закрыт пином
- Architecture: HIGH по паттернам compose/CI/healthz (официальные примеры); MEDIUM по layout-деталям (структура каталогов — discretion фазы, паттерн общепринят)
- Pitfalls: HIGH для 2/3/4/6/7 (доки/метаданные verbatim); MEDIUM для 1/5/8/9 (многократно наблюдаемая практика, не цитирована здесь)
- Провайдер-тиры seam (`classify-confidence --provider webfetch/pip`) формально LOW — компенсировано тем, что каждый факт привязан к первоисточнику (реестр/официальные доки), по прецеденту stack-research

**Research date:** 2026-11-18
**Valid until:** ~2026-12-18 (стабильные LTS-линии; патчи 5.2.x/DRF возможны — пины `==` защищают план; перепроверить при смене мажоров Django/DRF)

---

*Phase: 1-Фундамент — выбор стека и скелет проекта*
*Research: gsd-phase-researcher, 2026-11-18*
