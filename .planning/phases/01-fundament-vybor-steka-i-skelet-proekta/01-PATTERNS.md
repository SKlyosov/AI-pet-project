# Phase 1: Фундамент — выбор стека и скелет проекта - Pattern Map

**Mapped:** 2026-11-18
**Files analyzed:** 47 (45 new / 2 modified)
**Analogs found:** 0 / 45 файлов приложения — greenfield-репозиторий (ожидаемо и честно)

> **Greenfield-вердикт (проверено, не предположение).** `git ls-files` от 2026-11-18: в tracked-дереве только `.opencode/**` (тулинг GSD/OpenCode — JavaScript, «не часть приложения» по 01-CONTEXT.md, § Existing code Insights / Integration Points), `.planning/**` (планировочные документы), `AGENTS.md`, `README.md` (одна строка-плейсхолдер), `docs/PRD.md`. Файлов приложения (Python/Django/инфраструктура) — **ноль**. Скан диска (`dir /b` корня) и `git status --porcelain` дополнительных исходников не показал; каталогов `.claude/skills/` и `.agents/skills/` нет.
>
> **Следствие для планировщика:** каждый файл фазы 1 — seed собственного паттерна. Единственный copy-source для code — верbatim-примеры из `01-RESEARCH.md` (цитированы из официальных доков Docker/Django/GHA/django-redis/WhiteNoise/pytest-django); ниже для каждого файла указан точный диапазон строк. Для файлов документации существуют tracked-источники стиля (`docs/PRD.md`, `.planning/research/STACK.md`) — они приведены как doc-reference, НЕ как code-аналоги. Аналогов из `.opencode/**` не даём сознательно: чужая экосистема, зеркало тулинга, не приложение.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `docs/adr/0001-choice-of-stack.md` | documentation (ADR) | — (static) | `docs/PRD.md` — стиль русскояз. документации; контент: `.planning/research/STACK.md` + `01-CONTEXT.md` D-01…D-08 | doc-reference (не code-аналог) |
| `AGENTS.md` (modify) | documentation (repo rules) | — | сам файл — конвенции уже в нём | self |
| `README.md` (modify) | documentation | — | текущий однострочный плейсхолдер | self |
| `compose.yaml` | config (infrastructure) | — (service orchestration) | нет — seed | none |
| `Dockerfile` | config (build) | — | нет — seed | none |
| `entrypoint.sh` | utility | batch (migrate → collectstatic → gunicorn) | нет — seed | none |
| `.github/workflows/ci.yml` | config (CI) | batch (ruff → mypy → drift-check → pytest) | нет — seed | none |
| `config/settings/base.py` (+`config/__init__.py`, `config/settings/__init__.py`) | config | — (env-driven) | нет — seed | none |
| `config/settings/dev.py` | config | — | нет (наследует `base.py`) | none |
| `config/settings/prod.py` | config | — | нет (наследует `base.py`) | none |
| `config/settings/test.py` | config | — | нет (наследует `base.py`) | none |
| `config/urls.py` | route | request-response | нет — seed | none |
| `config/wsgi.py` | config | — (WSGI entrypoint) | нет — seed | none |
| `manage.py` (implied — деревом не показан, но нужен каждой команде research'а) | utility | — | нет — seed | none |
| `apps/core/__init__.py`, `apps/core/apps.py`, `apps/core/views.py` | controller (Django view) | request-response (SELECT 1 + cache ping) | нет — seed контроллера | none |
| `apps/{accounts,catalog,geo,listings,search,messaging,moderation}/` — 7 stub-приложений (`__init__.py` + `apps.py` каждый) | module placeholder | — | нет — seed | none |
| `templates/` (базовый SSR-шаблон) | component (SSR) | request-response (rendered) | нет — seed | none |
| `static/` (исходники CSS/логотип) | asset | — | нет — seed | none |
| `tests/__init__.py`, `tests/conftest.py` | test (fixtures) | — | нет — seed | none |
| `tests/test_health.py` | test | request-response (integration) | нет — seed | none |
| `scripts/verify_bootstrap.sh` (+ `.cmd` для Windows-хоста) | utility | batch (smoke SC-2/SC-4) | нет — seed | none |
| `requirements/base.txt` | config (deps) | — | нет — seed | none |
| `requirements/dev.txt` | config (deps) | — | нет — seed | none |
| `pyproject.toml` | config (tooling: ruff/mypy/pytest/django-stubs) | — | нет — seed | none |
| `.gitignore` | config | — | нет — seed | none |
| `.gitattributes` | config (eol=lf) | — | нет — seed | none |
| `.env.example` | config (secrets template) | — | нет — seed | none |
| `.dockerignore` | config | — | нет — seed | none |

## Pattern Assignments

Формат блока в greenfield-фазе: **Analog** = нет; **Copy-source** = точный диапазон строк `01-RESEARCH.md` (файл лежит рядом с PATTERNS.md); + паттерн-правила и привязанные pitfalls. Все указанные диапазоны сверены чтением 2026-11-18.

---

### `apps/core/views.py` (controller, request-response)

**Analog:** нет — seed. Этот файл становится каноническим аналогом для ВСЕХ будущих view/эндпоинтов проекта (фазы 5–6 SSR, DRF-эндпоинты фаз 7–8).

**Copy-source:** `01-RESEARCH.md` «Health endpoint», строки 380–399; Pattern 2 «Health-check без раскрытия внутренностей», строки 274–278.

```python
# 01-RESEARCH.md:380-399 — копировать как основу
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

**Паттерн-правила:** ответ БЕЗ внутренностей (никаких версий/хостов/DSN/стектрейсов — Security Domain, строка 698); 503 при недоступности любой зависимости; GET без параметров (V5 Input Validation — неприменим по определению).

---

### `compose.yaml` (config, service orchestration)

**Analog:** нет — seed.

**Copy-source:** `01-RESEARCH.md` «compose.yaml (ключевые фрагменты…)», строки 406–455 (healthcheck db — verbatim из docs.docker.com, пример официально использует postgres:18).

```yaml
# 01-RESEARCH.md:441-446 — ядро паттерна готовности сервисов
    depends_on:
      db:
        condition: service_healthy       # verbatim-паттерн доков
        restart: true                    # verbatim-паттерн доков
      cache:
        condition: service_healthy
```

**Паттерн-правила / pitfalls:**
- `$$`-экранирование в healthcheck: `pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}` — Pitfall 3, строки 337–341 (web вечно ждёт `service_healthy`, если написать `${}`).
- Порты db/cache публиковать ТОЛЬКО на `127.0.0.1` хоста (Security Domain, строка 702).
- `${POSTGRES_PASSWORD:?set in .env}` — compose падает без значения (строка 699).
- Анти-паттерны: жёсткий `depends_on` без condition (строка 300), sleep-петли вместо healthchecks (строка 301).

---

### `Dockerfile` + `entrypoint.sh` (config / utility, batch)

**Analog:** нет — seed.

**Copy-source:** `01-RESEARCH.md` «Dockerfile + entrypoint», строки 459–477.

```bash
# 01-RESEARCH.md:471-477 — копировать как есть
#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
```

**Паттерн-правила / pitfalls:**
- Web-образ ТОЛЬКО `python:3.13-slim` (glibc): psycopg-binary — manylinux-колёса, на musl (alpine) не ставится — Anti-Pattern, строка 299, Assumption A8 (строка 610). `*-alpine` — только db/cache.
- `exec gunicorn` — обязательный (PID 1 / сигнал завершения).
- CRLF-защита: `.gitattributes` со строкой `* text=auto eol=lf` — Pitfall 5, строки 349–353 (Windows-хост! `/bin/sh^M: not found`).
- Healthcheck web-контейнера — python-urllib one-liner (в slim нет curl) — строки 448–451, Assumption A3.

---

### `config/settings/base.py` (config, env-driven)

**Analog:** нет — seed. Канонический аналог для всей будущей конфигурации (фазы 2+ добавляют настройки сюда).

**Copy-source:** `01-RESEARCH.md` Pattern 1 «Split settings», строки 253–272; CACHES verbatim из README django-redis — строки 481–492; WhiteNoise verbatim — строки 496–511.

```python
# 01-RESEARCH.md:260-272 — копировать как основу (секреты ТОЛЬКО из env)
import environ

env = environ.Env()
DATABASES = {"default": env.db("DATABASE_URL")}
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://cache:6379/0"),
    }
}
SECRET_KEY = env("DJANGO_SECRET_KEY")
```

**Паттерн-правила:** INSTALLED_APPS ссылается на `apps.*` (tree, строка 231); WhiteNoise middleware СРАЗУ после SecurityMiddleware и STORAGES `whitenoise.storage.CompressedManifestStaticFilesStorage` (строки 498–510); dev — `whitenoise.runserver_nostatic` в начало INSTALLED_APPS (строка 510). Анти-паттерн: SECRET_KEY/пароли в settings-файлах или git (строка 303).

---

### `config/settings/{dev,prod,test}.py` (config)

**Analog:** нет — наследуют `base.py`.

**Copy-source:** выбор через `DJANGO_SETTINGS_MODULE` — `01-RESEARCH.md` строка 255; дерево — строка 232–234.

**Паттерн-правила / pitfalls:**
- `test.py`: `WHITENOISE_AUTOREFRESH = True` — Pitfall 7, строки 362–364 (замедление pytest); быстрые хэшеры; env-дефолты CI (Wave 0 gaps, строка 673).
- `prod.py`: `DEBUG=False` + SECURITY-настройки; `ALLOWED_HOSTS` из env обязательно включая `localhost`, `web`, `127.0.0.1` — Pitfall 4, строки 343–347 (иначе `curl /healthz` → 400).
- dev-БД фазы 1 — одноразовая (см. ADR-блок ниже, Pitfall 1).

---

### `config/urls.py` (route, request-response)

**Analog:** нет — seed.

**Copy-source:** дерево структуры `01-RESEARCH.md` строка 235: `path("healthz/", ...)`, `path("admin/", ...)` — импорт view из `apps.core.views`. Admin-роут обязателен (D-02: Django Admin — админ-слой проекта).

---

### `config/wsgi.py` + `manage.py` (config / utility)

**Analog:** нет — seed.

**Copy-source:** стандартный scaffold `django-admin startproject`, адаптированный: проект называется `config`, settings — `config.settings.base` (tree, строки 229–236; entrypoint ссылается `config.wsgi:application`, строка 476).

---

### `apps/{accounts,catalog,geo,listings,search,messaging,moderation}/` — 7 stub-приложений (module placeholder)

**Analog:** нет — seed. `apps/accounts/` — будущий канонический аналог Django-app layout для Phase 2 (custom User); остальные — для своих фаз (3/4/7/8/9).

**Copy-source:** дерево `01-RESEARCH.md` строки 237–245; D-04 (CONTEXT.md) — граница модуля = владение своими таблицами; Pattern 3 «Границы модулей = границы таблиц», строки 280–284.

**Паттерн-правила:** stub = `__init__.py` + `apps.py` (пустые, без моделей — Pattern 4, строка 288: никаких фейковых моделей для «первой миграции»); дисциплина импортов с первого дня: `messaging` НЕ делает `from apps.listings.models import ...` — только через сервис-функцию владельца (строки 282–283).

---

### `tests/conftest.py` + `tests/test_health.py` (test)

**Analog:** нет — seed. Канонический аналог тестового layout'а для всех последующих фаз (Phase 2 добавит factory_boy-фабрики рядом).

**Copy-source:** Wave 0 gaps `01-RESEARCH.md` строки 670–677; команды прогона — строки 652–653 (`docker compose run --rm web pytest -x -q`); мапа SC→тестам — строки 655–663.

**Паттерн-правила:** `DJANGO_SETTINGS_MODULE = "config.settings.test"` (через pyproject, не дублировать); `test_health.py` — integration через pytest-django (`django_db`), проверяет 200 от `/healthz` при живых db+cache; host-Python отсутствует — все команды через `docker compose` (Pitfall 8, строки 366–370).

---

### `scripts/verify_bootstrap.{sh,cmd}` (utility, batch)

**Analog:** нет — seed. Первый «верификационный скрипт» проекта — будущий аналог для скриптов приёмки других фаз.

**Copy-source:** `01-RESEARCH.md` строка 660 (команда SC-2: `docker compose down -v && docker compose up -d --wait && curl -fsS http://localhost:8000/healthz`) и строка 663 (SC-4: `migrate` + `showmigrations`, все `[X]`). Assumption A4 (строка 606): fallback при отсутствии `--wait` — polling curl.

---

### `pyproject.toml` (config, tooling)

**Analog:** нет — seed; единственный дом конфигов тулинга (ruff/mypy/pytest/django-stubs).

**Copy-source:** `01-RESEARCH.md` строки 515–530.

```toml
# 01-RESEARCH.md:516-529 — копировать как основу
[tool.pytest]
DJANGO_SETTINGS_MODULE = "config.settings.test"   # native TOML для pytest 9+

[tool.ruff]
target-version = "py313"

[tool.mypy]
python_version = "3.13"
plugins = ["mypy_django_plugin.main"]
ignore_missing_imports = true                     # non-strict старт (D-06)

[tool.django-stubs]
django_settings_module = "config.settings.test"
```

**Паттерн-правила:** НЕ `[tool.pytest.ini_options]`, а `[tool.pytest]` — pytest 9.0+ (State of the Art, строка 590); mypy пинится в 1.19.x — Pitfall 2, строки 331–335 (django-stubs 5.2.9: `compatible-mypy: mypy>=1.13,<1.20`; mypy 2.x резолвится, но вне тестируемого диапазона).

---

### `requirements/{base,dev}.txt` (config, deps)

**Analog:** нет — seed.

**Copy-source:** `01-RESEARCH.md` строки 119–138 — точные пины `==` из успешной пробы разрешения (py3.13/manylinux): Django 5.2.19, DRF 3.18.3, gunicorn 27.0.1, `psycopg[binary]` 3.3.9, django-redis 7.0.0, whitenoise 6.12.0, django-environ 0.14.0 / pytest 9.2.0, pytest-django 4.14.0, ruff 0.17.5, **mypy==1.19.1**, django-stubs 5.2.9, coverage 7.17.3, factory_boy 3.3.3.

**Паттерн-правила:** пины `==` обязательны — и для кэша pip в CI (setup-python README, строка 581), и для supply-chain (Security Domain, строка 703); `dev.txt` начинается с `-r base.txt`.

---

### `.github/workflows/ci.yml` (config, CI batch)

**Analog:** нет — seed; будущий аналог для всех новых workflow.

**Copy-source:** `01-RESEARCH.md` строки 534–581 — готовый workflow: `on: [push, pull_request]`, `permissions: contents: read`, `services:` postgres:18 + redis:8, `setup-python@v7` + `cache: 'pip'` + `cache-dependency-path: requirements/*.txt`, ступени отдельными steps: Lint → Typecheck → Migrations drift check → Tests.

**Паттерн-правила / pitfalls:** каждая ступень — отдельный step (падение любой краснит job — SC-3, строка 581); `makemigrations --check --dry-run` ДО pytest — Pitfall 9, строки 372–374 (тихий дрейф миграций); один job, не matrix — Open Questions №3, строка 630.

---

### `docs/adr/0001-choice-of-stack.md` (documentation, ADR)

**Analog:** code-аналога нет. Doc-reference (tracked): `docs/PRD.md` — конвенции русскоязычной документации проекта: тело на русском, `#`-заголовки секций, плоские списки без нумерации там, где порядок не важен (см. `docs/PRD.md` строки 1–9, 38–44).

**Copy-source контента:** `.planning/research/STACK.md` — варианты A/B/C с tradeoffs (строка 7 — правило репозитория: выбор за пользователем; B = Django-альтернатива в терминах research'а) + `01-CONTEXT.md` D-01…D-08 (обоснования) и § Specifics (строка 70: выбран B именно из-за Django Admin).

**Паттерн-правила:** обязателен фикс Pitfall 1 (строки 325–329): dev-БД фазы 1 одноразовая, custom User — Phase 2 ДО появления пользовательских данных + пересоздание dev-тома (`docker compose down -v`) — решение осознанное. Этот файл — seed ADR-серии (`docs/adr/NNNN-*.md`).

---

### `.gitignore`, `.gitattributes`, `.env.example`, `.dockerignore` (config)

**Analog:** нет — seed.

**Copy-source:** дерево `01-RESEARCH.md` строки 214–216 (`.gitignore`: .env, `__pycache__`, staticfiles/, .venv/; `.gitattributes`: `* text=auto eol=lf`; `.env.example`: все переменные с безопасными dev-дефолтами). Переменные окружения — из compose-блока строки 411–414 (POSTGRES_DB/USER/PASSWORD, DATABASE_URL/REDIS_URL/DJANGO_SECRET_KEY) и CI env строки 559–562. `${POSTGRES_PASSWORD:?set in .env}`-паттерн — строка 699.

---

### `AGENTS.md` (modify) и `README.md` (modify)

**Analog:** сами файлы.

**Copy-source:** правило «AGENTS.md обновляется тем же коммитом, что приносит тулинг/структуру» — AGENTS.md § Keeping this file useful + `01-RESEARCH.md` строка 61 (задача обязана войти в план). Команды для фиксации: `docker compose up`, `docker compose run --rm web pytest -x -q`, `ruff check .`, `mypy .` — docker-first workflow, Pitfall 8, строки 366–370 (на хосте только `py` 3.14, `python`/`pip` не в PATH). README — «как поднять одной командой» по SC-2 (строки 51, 206).

**Паттерн-правила:** «Verified facts only; omit anything you can't check» (AGENTS.md) — в AGENTS.md попадают только реально проверенные команды; README на русском.

---

## Shared Patterns

Сквозные конвенции, применяемые ко ВСЕМ планам фазы (и наследуемые фазами 2–9). Это единственные «паттерны», реально существующие в репозитории сегодня.

### Git-конвенции репозитория
**Source (tracked):** `AGENTS.md`; `.opencode/rules/git-main-protection.md` (git-tracked ✓).
**Apply to:** каждый план/коммит фазы.
- Нет прямых коммитов в `main`; ветки `feat/<name>`, `fix/<name>`, `chore/<name>` (фаза 1 целиком логично ложится на `chore/` или `feat/`-ветку).
- Conventional Commits для сообщений.
- ⚠️ `.opencode/rules/git-new-files.md` существует на диске, но сейчас НЕ закоммичен (`git status`: untracked) — при цитировании в планах помечать как правило-на-диске; в GSD-потоке коммитит оркестратор после подтверждения пользователем.

### Язык документации
**Source (tracked):** `docs/PRD.md`, `.planning/**`.
**Apply to:** ADR, README, AGENTS.md, комментарии в code.
- Тело документов на русском; технические термины/имена команд/пути — как есть (английские). Заголовки шаблонов GSD — английские (как в этом файле).

### Security baseline (ASVS L1)
**Source:** `01-RESEARCH.md` Security Domain, строки 681–704.
**Apply to:** settings, compose, CI, .env.example, healthz.
- Секреты только из env; `.env` в `.gitignore`; `.env.example` без секретов; dev-дефолты безопасные.
- Health-check без раскрытия внутренностей; `DEBUG=False` в prod; `ALLOWED_HOSTS` явный список; порты db/cache только `127.0.0.1` на хосте.

### Healthcheck/readiness-конвенции
**Source:** `01-RESEARCH.md` строки 291–294 (Pattern 5), 337–341 (Pitfall 3).
**Apply to:** compose.yaml, ci.yml (services), verify_bootstrap.
- `depends_on` с `condition: service_healthy` + `restart: true`; `$$`-экранирование переменных в healthcheck-командах; никаких sleep-петель.

### Seed map — что станет аналогом для последующих фаз
**Apply to:** PATTERNS.md фаз 2–9 (pattern-mapper'ам будущих фаз ссылаться сюда).

| Seed-файл фазы 1 | Каноническим аналогом становится для |
|------------------|--------------------------------------|
| `apps/core/views.py` | все Django view / эндпоинты (фазы 5–8), DRF-представления |
| `config/settings/base.py` | вся будущая конфигурация (в т.ч. добавки фаз 2+: SESSION_ENGINE, S3-Storage фазы 5) |
| `tests/conftest.py` + `tests/test_health.py` | весь тестовый layout; рядом появятся factory_boy-фабрики (Phase 2) |
| `apps/accounts/` (stub → custom User) | layout каждого доменного app'а (модели/сервисы/миграции фаз 2–9) |
| `compose.yaml` / `Dockerfile` / `entrypoint.sh` | любые новые сервисы/инфраструктура (MinIO в Phase 5) |
| `.github/workflows/ci.yml` | любые новые workflow/ступени |
| `pyproject.toml` | любые новые инструменты (конфиг в одном доме) |
| `docs/adr/0001-choice-of-stack.md` | ADR-серия (`docs/adr/NNNN-*.md`) |

## No Analog Found

Все 45 новых файлов приложения не имеют аналога в codeбазе — по одной причине:

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| все строки «none» из § File Classification | — | — | Greenfield: в tracked-дереве нет ни одного файла приложения (проверено `git ls-files` 2026-11-18). Планировщик использует copy-source'ы из `01-RESEARCH.md` по карте § Pattern Assignments. |

**Явный отказ от ложных аналогов:** `.opencode/**` — тулинг GSD/OpenCode на JavaScript; по CONTEXT.md (§ Integration Points) «не часть приложения». Клоны/шаблоны GSD (`templates/`, `workflows/`) не являются источником паттернов Django-приложения и в PATTERNS.md не цитируются. Зеркал `.gsd/capabilities/` в репозитории нет — tracked-source gate пройден тривиально (0 кандидатов).

## Metadata

**Analog search scope:** весь tracked-источник репозитория — `git ls-files` (~430 файлов: `.opencode/**`, `.planning/**`, `AGENTS.md`, `README.md`, `docs/PRD.md`) + скан корня диска (`dir /b`) + `git status --porcelain` (untracked: `.idea/`, `.opencode/rules/git-new-files.md`, `.planning/research/.cache/` — ни один не является источником паттернов приложения).
**Project skills:** каталоги `.claude/skills/` и `.agents/skills/` отсутствуют; `.opencode/skills/` — скиллы GSD-тулинга, к приложения не относятся.
**Tracked-source gate (#3645):** все названные reference-пути (`docs/PRD.md`, `.planning/research/STACK.md`, `AGENTS.md`, `README.md`, `.opencode/rules/git-main-protection.md`) проверены через `git ls-files` — tracked ✓; единственное исключение помечено в тексте (`git-new-files.md` — untracked).
**Files scanned:** ~430 tracked / 0 application-source.
**Pattern extraction date:** 2026-11-18

---

*Phase: 1-Фундамент — выбор стека и скелет проекта*
*Patterns: gsd-pattern-mapper (greenfield pass)*
