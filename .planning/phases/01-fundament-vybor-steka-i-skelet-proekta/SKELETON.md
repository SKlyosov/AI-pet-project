# Walking Skeleton — Private Classifieds (Частные объявления)

**Phase:** 1
**Generated:** 2026-11-18

## Capability Proven End-to-End

> Разработчик поднимает свежий клон одной командой `docker compose up -d --build --wait` и получает: ответ 200 от `/healthz` (реальный `SELECT 1` в PostgreSQL + cache-ping в Redis) и SSR-корневую страницу со счётчиком просмотров, растущим при перезагрузке (реальный write+read в Redis).

Маршруты скелета: `/healthz` (JSON health-check), `/` (SSR-страница со счётчиком `core:home:hits`), `/admin/` (Django Admin — вход появится с суперпользователем в Phase 2).

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Python / Django 5.2 LTS + Django REST Framework (D-01) | Явный выбор пользователя из вариантов A/B/C; ADR-0001 `docs/adr/0001-choice-of-stack.md`; LTS до апр. 2028; Django Admin закрывает админ-CRUD PRD (D-02) |
| Data layer | PostgreSQL 18 (psycopg[binary] 3.3.9) + Redis 8 (django-redis 7.0.0) | Единственная RDBMS по D-01; Redis — кэш/сессии/лимиты; версии verified-пробой PyPI |
| Auth | Не в скелете | Phase 2 вводит custom User ДО появления пользовательских данных; dev-БД фазы 1 — одноразовая (ADR-0001, Pitfall 1 research'а) |
| Rendering | SSR через Django templates (D-03); DRF — точечно для JSON API позже | SEO-страницы фаз 5–6 без JS-фреймворка; SPA не строим |
| Server | gunicorn 27 (WSGI) в python:3.13-slim; WhiteNoise для статики | D-08: ASGI отложен до realtime (v2+); nginx не нужен на старте (upgrade-путь WhiteNoise) |
| Deployment target | docker compose (dev): db + cache + web с healthchecks; `depends_on: condition: service_healthy` | SC-2 «одна команда»; прод-деплой вне scope фазы 1 |
| Directory layout | `config/` (проект: settings/{base,dev,prod,test}, urls, wsgi) + `apps/<домен>` (8 модулей: core + 7 доменных) | D-04 модульный монолит; граница модуля = владение своими таблицами |
| CI | GitHub Actions, один job: ruff → mypy → makemigrations --check → pytest (D-06) | Каждая ступень — отдельный step; services postgres:18 + redis:8 |
| Python | 3.13 (наибольшая общая версия всего набора зависимостей; mypy запинен 1.19.1 под django-stubs 5.2.9) | Verified матрицей PyPI/wheel-METADATA (research § Standard Stack) |

## Stack Touched in Phase 1

- [x] Project scaffold (Django-проект config/, manage.py, requirements с пинами ==, pyproject: ruff/mypy/pytest/django-stubs)
- [x] Routing — реальные маршруты `/healthz`, `/`, `/admin/` в config/urls.py
- [x] Database — реальный read (`SELECT 1` в healthz) и воспроизводимая первая миграция на чистом томе (contrib-миграции; доменные — фазы 2–9)
- [x] UI — корневая SSR-страница со счётчиком просмотров (инкремент виден перезагрузкой; write+read в Redis через django cache API)
- [x] Deployment — локальный полный стек одной командой `docker compose up -d --build --wait`; приёмка `scripts/verify_bootstrap.cmd`

## Out of Scope (Deferred to Later Slices)

- Авторизация/сессии пользователей, custom User — Phase 2 (до появления пользовательских данных; dev-том пересоздаётся `docker compose down -v`)
- Доменные модели и миграции (accounts/catalog/geo/listings/search/messaging/moderation — каркасы без моделей)
- Объектное хранилище MinIO/S3 — Phase 5 (фотографии)
- nginx, CDN, ASGI/WebSocket, Redis-сессии — по мере необходимости (SESSION_ENGINE закомментирован в research)
- Прод-деплой и TLS — вне фазы 1 (SECURE_SSL_REDIRECT/HSTS закомментированы в prod.py)
- Нагрузочные/сквозные приёмочные тесты — фазы 7 и 10

## Subsequent Slice Plan

Каждая следующая фаза добавляет один вертикальный срез поверх скелета, не меняя архитектурных решений:

- Phase 2: аккаунты — custom User + auth + профиль (PII-политика с первого дня)
- Phase 3: справочники администратора в Django Admin (рубрикатор с защитой от циклов, города)
- Phase 4: объявления — CRUD, черновики, атомарная квота ≤10, hard delete, инварианты схемы
- Phase 5: фотографии — S3-совместимое хранилище (MinIO добавится в compose), ресайзы
- Phase 6: публичные SSR-страницы с SEO-URL (Django templates — как / скелета)
- Phase 7: полнотекстовый поиск (PG FTS, русская морфология) + фильтры/пагинация
- Phase 8: мессенджер (DRF API точечно — как заложено D-03) + e-mail-уведомления
- Phase 9: модерация через Django Admin + audit log
- Phase 10: security-проход и сквозная приёмка
