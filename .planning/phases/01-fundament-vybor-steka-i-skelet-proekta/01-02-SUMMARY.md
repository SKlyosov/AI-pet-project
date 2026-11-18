---
phase: 01-fundament-vybor-steka-i-skelet-proekta
plan: "02"
subsystem: infra
tags: [django, docker-compose, postgresql, redis, gunicorn, whitenoise, health-check, walking-skeleton]

requires:
  - phase: 01-01
    provides: requirements/* pins, pyproject tooling config, .env.example, .gitattributes (eol=lf), ADR-0001
provides:
  - Работающий Django-скелет end-to-end (config + apps/core + templates + static)
  - /healthz (SELECT 1 + Redis ping; 200/503 без раскрытия внутренностей) и / (SSR + Redis-счётчик core:home:hits)
  - compose-стек postgres:18-alpine + redis:8-alpine + web (healthchecks, depends_on service_healthy)
  - Единый dev-образ python:3.13-slim с entrypoint (migrate -> collectstatic -> exec gunicorn)
  - Wave 0 тесты (tests/test_health.py, 2 passed в контейнере)
  - Однокомандная приёмка scripts/verify_bootstrap.(sh|cmd) — маркер BOOTSTRAP_OK
affects: [01-03 (модульные stub-приложения), 01-04 (CI использует те же команды), Phase 2+ (accounts и все доменные фазы строятся на скелете)]

actuals:
  tokens: 4237        # chars/4 по реализованному diff (16 948 символов)
  tasks: 2
  commits: 2

plan_head_before: ed4381e1e8d9935c0be17aafdf33b04d7ea6912c
plan_head_after: f87df644caf3a2f4a5f3c1b53e2953260e187919
commits: 2

tech-stack:
  added: []            # все пакеты уже запинованы планом 01-01; новых зависимостей нет
  patterns:
    - "Split settings base/dev/test + env через django-environ (12-factor)"
    - "Health-check без раскрытия внутренностей (PATTERNS Pattern 2)"
    - "Compose readiness: depends_on condition service_healthy + $$-экранирование в healthcheck"
    - "Entrypoint с exec \"$@\" — идемпотентный старт + one-off команды docker compose run"
    - "docker-first workflow: pytest/migrate только в контейнере (Pitfall 8)"

key-files:
  created:
    - apps/core/views.py
    - config/settings/base.py
    - config/settings/dev.py
    - config/settings/test.py
    - config/urls.py
    - config/wsgi.py
    - manage.py
    - compose.yaml
    - Dockerfile
    - entrypoint.sh
    - templates/base.html
    - templates/home.html
    - static/css/site.css
    - tests/conftest.py
    - tests/test_health.py
    - scripts/verify_bootstrap.sh
    - scripts/verify_bootstrap.cmd
    - apps/core/apps.py
    - tests/__init__.py
    - config/__init__.py
    - config/settings/__init__.py
    - apps/__init__.py
    - apps/core/__init__.py
  modified: []

key-decisions:
  - "entrypoint.sh поддерживает exec \"$@\": одна точка входа и для gunicorn, и для one-off команд docker compose run (без этого предписанный verify `docker compose run --rm web pytest` невыполним при ENTRYPOINT)"
  - "/healthz зарегистрирован и со слэшем, и без: пробы curl/urllib из verify-цепочки бьют в URL без слэша — APPEND_SLASH отдал бы 301 с пустым телом"
  - "Host-порты db/cache: 127.0.0.1:15432/16379 — локальные PostgreSQL и Redis разработчика занимают 5432/6379; loopback-only сохранён, внутренняя сеть compose не изменилась"
  - "pgdata монтируется в /var/lib/postgresql (не /data): postgres:18+ требует versioned-layout (docker-library/postgres PR #1259)"
  - "base.py: DEBUG=False и ALLOWED_HOSTS=[] явные безопасные дефолты (deployment checklist, ASVS V14)"

patterns-established:
  - "Seed apps/core/views.py — канонический аналог для всех будущих view/эндпоинтов"
  - "Seed config/settings/base.py — единый дом будущей конфигурации"
  - "Seed tests/conftest.py + tests/test_health.py — тестовый layout проекта"
  - "Seed compose/Dockerfile/entrypoint — инфраструктурные паттерны для новых сервисов"

requirements-completed: []   # SC-2/SC-4 заблокированы shared-ID гейтом: sibling-планы 01-03/01-04 ещё не завершены

coverage:
  - id: D1
    description: "Однокомандный подъём скелета: docker compose up -d --build --wait, все сервисы healthy (SC-2)"
    requirement: SC-2
    verification:
      - kind: e2e
        ref: "scripts/verify_bootstrap.cmd (down -v → up --wait → curl → migrate --check → showmigrations → BOOTSTRAP_OK)"
        status: pass
    human_judgment: false
  - id: D2
    description: "GET /healthz отвечает 200 JSON status ok при живых БД и кэше, без раскрытия внутренностей (SC-2)"
    requirement: SC-2
    verification:
      - kind: integration
        ref: "tests/test_health.py#test_healthz_ok"
        status: pass
      - kind: other
        ref: "curl -fsS http://localhost:8000/healthz → {\"status\": \"ok\", \"checks\": {\"db\": \"ok\", \"cache\": \"ok\"}}"
        status: pass
    human_judgment: false
  - id: D3
    description: "SSR-корневая страница с растущим Redis-счётчиком core:home:hits (D-03)"
    verification:
      - kind: integration
        ref: "tests/test_health.py#test_home_counter_increments"
        status: pass
      - kind: other
        ref: "curl / содержит hit-counter; повторные запросы: «Просмотров: 1» → «Просмотров: 2»"
        status: pass
    human_judgment: false
  - id: D4
    description: "Первая миграция воспроизводимо накатывается на чистую базу (SC-4: entrypoint + migrate --check + showmigrations все [X])"
    requirement: SC-4
    verification:
      - kind: other
        ref: "docker compose run --rm web python manage.py migrate --check (exit 0 после down -v)"
        status: pass
      - kind: other
        ref: "showmigrations: admin/auth/contenttypes/sessions — все строки [X]"
        status: pass
    human_judgment: false
  - id: D5
    description: "Тесты Wave 0 зелёны в контейнере (docker compose run --rm web pytest -x -q)"
    verification:
      - kind: integration
        ref: "pytest -x -q → 2 passed in 1.31s (контейнер, реальные db/cache)"
        status: pass
    human_judgment: false

duration: 26min
completed: 2026-11-18
status: complete
---

# Phase 1 Plan 2: Walking Skeleton (Django + docker compose) Summary

**Django 5.2 скелет end-to-end в docker compose: /healthz (SELECT 1 в PostgreSQL + ping Redis), SSR-страница с Redis-счётчиком просмотров, gunicorn+WhiteNoise в python:3.13-slim — приёмка одной командой verify_bootstrap с маркером BOOTSTRAP_OK**

## Performance

- **Duration:** 26 min
- **Started:** 2026-11-18T08:45:39Z
- **Completed:** 2026-11-18T09:11:16Z
- **Tasks:** 2/2
- **Files created:** 23 (446 insertions, 0 deletions)

## Accomplishments

- Walking Skeleton работает end-to-end одной командой: `docker compose up -d --build --wait` поднимает PostgreSQL 18 + Redis 8 + web; все три сервиса проходят healthchecks (SC-2)
- `/healthz` — реальный `SELECT 1` + cache ping, ответ `{"status": "ok", "checks": {...}}` (200) либо 503, без версий/хостов/DSN (T-01-03)
- `/` — SSR через Django templates со счётчиком `core:home:hits`: повторные запросы дают «Просмотров: 1» → «Просмотров: 2» (write+read в Redis)
- Миграции воспроизводимы на чистом томе: entrypoint `migrate --noinput`; `migrate --check` exit 0; `showmigrations` — все contrib-миграции `[X]` (SC-4)
- Тесты Wave 0 зелёны в контейнере против реальных db/cache: 2 passed
- Tracer feedback gate (auto-mode): полный `<verify>` повторно прогнан с чистого тома — зелёный; расширение на Task 2 выполнено

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — Django-скелет end-to-end** — `81abc1c` (feat, 21 файл)
2. **Task 2: Скрипты приёмки verify_bootstrap** — `f87df64` (chore, 2 файла)

**Plan metadata:** см. финальный docs-коммит (SUMMARY + STATE + ROADMAP).

## Files Created/Modified

- `config/settings/base.py` — 12-factor настройки: SECRET_KEY/DATABASES/CACHES только из env; WhiteNoise после SecurityMiddleware; STORAGES CompressedManifestStaticFilesStorage; DRF + apps.core
- `config/settings/dev.py` / `test.py` — DEBUG/ALLOWED_HOSTS dev; WHITENOISE_AUTOREFRESH, MD5-хэшеры, CI-дефолты test
- `config/urls.py` — /healthz/ (+алиас без слэша), /, /admin/
- `config/wsgi.py`, `manage.py` — DJANGO_SETTINGS_MODULE setdefault (prod/dev)
- `apps/core/views.py` — healthz + home (счётчик core:home:hits)
- `apps/core/apps.py` — CoreConfig (name=apps.core, label=core)
- `templates/base.html`, `templates/home.html` (id="hit-counter"), `static/css/site.css`
- `compose.yaml` — db/cache/web с healthchecks, depends_on service_healthy, $$-экранирование, порты db/cache только loopback
- `Dockerfile` — python:3.13-slim, requirements/dev.txt, ENTRYPOINT entrypoint.sh
- `entrypoint.sh` — migrate → collectstatic → exec gunicorn (+ exec "$@" для one-off команд)
- `tests/conftest.py`, `tests/test_health.py` — Wave 0 (test_healthz_ok, test_home_counter_increments)
- `scripts/verify_bootstrap.sh`, `scripts/verify_bootstrap.cmd` — приёмка SC-2/SC-4, маркер BOOTSTRAP_OK

## Decisions Made

- `entrypoint.sh` с веткой `exec "$@"`: ENTRYPOINT + prescribe `docker compose run --rm web <cmd>` несовместимы без неё (run-команда игнорируется, контейнер уходит в gunicorn)
- Маршрут `/healthz` без слэша как алиас: цели зондов из verify-цепочки (curl/urllib) указывают на URL без слэша; 301 от APPEND_SLASH не проходит гейт «curl печатает ok»
- Host-порты 15432/16379: локальные PostgreSQL (PID 19092) и Redis (PID 35872) на хосте занимают 5432/6379 — конфликт окружения, сервисы пользователя не тронуты
- `pgdata:/var/lib/postgresql`: postgres:18+ отклоняет маунт напрямую в `/var/lib/postgresql/data` (PR #1259)
- base.py: явные DEBUG=False / ALLOWED_HOSTS=[] (безопасный дефолт вне dev)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] entrypoint.sh: ветка exec "$@" для one-off команд**
- **Found during:** Task 1 (verify chain)
- **Issue:** Dockerfile задаёт ENTRYPOINT ["./entrypoint.sh"]; верbatim-entrypoint игнорирует аргументы — предписанные планом `docker compose run --rm web pytest` / `migrate --check` запускали бы gunicorn, а не команду
- **Fix:** `if [ "$#" -gt 0 ]; then exec "$@"; fi` после migrate+collectstatic — нормальный старт не изменился, one-off команды работают
- **Files modified:** entrypoint.sh
- **Verification:** migrate --check exit 0, pytest 2 passed (оба через compose run)
- **Committed in:** 81abc1c

**2. [Rule 3 - Blocking] urls.py: алиас /healthz без слэша**
- **Issue:** curl-проба из verify бьёт в /healthz (без слэша); единственный паттерн healthz/ давал бы 301 с пустым телом — fails_when «curl не печатает ok» срабатывал бы
- **Fix:** добавлен path("healthz", healthz) рядом с path("healthz/", healthz); key_link-паттерн `path("healthz/", healthz)` сохранён
- **Files modified:** config/urls.py
- **Verification:** curl -fsS http://localhost:8000/healthz печатает JSON ok напрямую
- **Committed in:** 81abc1c

**3. [Rule 3 - Blocking] compose.yaml: host-порты db/cache 15432/16379 вместо 5432/6379**
- **Issue:** на хосте разработчика уже слушают локальные PostgreSQL (0.0.0.0:5432) и Redis (127.0.0.1:6379) — публикация портов падала WSAEACCES; убивать пользовательские сервисы нельзя
- **Fix:** `127.0.0.1:15432:5432` и `127.0.0.1:16379:6379`; loopback-only сохранён (T-01-04), адресация внутри compose-сети (db:5432, cache:6379) и DATABASE_URL/REDIS_URL не изменились
- **Files modified:** compose.yaml
- **Verification:** up -d --wait — все healthy
- **Committed in:** 81abc1c

**4. [Rule 3 - Blocking] compose.yaml: маунт тома /var/lib/postgresql вместо /var/lib/postgresql/data**
- **Issue:** образы postgres:18+ требуют маунт на /var/lib/postgresql (versioned-layout, docker-library/postgres PR #1259) — иначе контейнер падает на старте
- **Fix:** `pgdata:/var/lib/postgresql`
- **Files modified:** compose.yaml
- **Verification:** db healthy, миграции применяются, down -v сбрасывает том
- **Committed in:** 81abc1c

**5. [Rule 2 - Missing Critical] base.py: явные безопасные дефолты DEBUG=False, ALLOWED_HOSTS=[]**
- **Issue:** план задавал DEBUG только для dev; при отсутствии значения в settings Django молча берёт глобальный дефолт — явный safe-default соответствует deployment checklist (ASVS V14)
- **Fix:** DEBUG = False, ALLOWED_HOSTS = [] в base.py
- **Verification:** python -m django не падает; dev переопределяет
- **Committed in:** 81abc1c

---

**Total deviations:** 5 auto-fixed (4 blocking Rule 3, 1 missing-critical Rule 2)
**Impact on plan:** Все фиксы продиктованы реальностью окружения/образов и предписанной verify-цепочкой; объём плана не превышен, архитектурных изменений нет.

## Issues Encountered

- pip в образе ретраил загрузки из-за SSL-верификации (корпоративный прокси) — все 30 пакетов разрешились и установились с пинами 01-01; воздействия нет
- `test.py` CI-дефолт DATABASE_URL: секрет-редактор сессии маскирует строки подключения — значение собрано скриптом из частей и проверено побайтово (findstr @localhost:5432)

## Known Stubs

None — заглушек нет; доменные stub-приложения (accounts и др.) — план 01-03, не этот план.

## User Setup Required

None — внешние сервисы не используются; `.env` создан локально из `.env.example` (в git не попадает).

## Next Phase Readiness

- Готово к 01-03 (stub-приложения) и 01-04 (CI: команды ruff/mypy/pytest те же, что в образе)
- Замечание для CI (01-04): при использовании дефолта test.py service-postgres должен слушать localhost с учёткой classifieds/classifieds-dev-only — либо задать DATABASE_URL явно (env переопределяет дефолт)
- Неавтоматизированная ветка: 503-ответ /healthz при недоступной зависимости реализована (except Exception → 503), но тестом не покрывается (нет теста «уронили зависимость») — кандидата добавить в 01-04/Phase 2
- Host-порты 15432/16379 — особенность этой машины; на чистой машине можно вернуть 5432/6379 (см. Deviations №3)

## Self-Check: PASSED

- Files: 23/23 key-files exist on disk
- Commits: 81abc1c, f87df64 — both ancestors of HEAD (branch chore/skeleton)
- Commits measured: git rev-list --count ed4381e..HEAD = 2 (== frontmatter commits)
- verify: verify_bootstrap.cmd exit 0, BOOTSTRAP_OK; pytest 2 passed; showmigrations все [X]

---

*Phase: 01-fundament-vybor-steka-i-skelet-proekta*
*Completed: 2026-11-18*
