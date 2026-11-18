---
phase: 01-fundament-vybor-steka-i-skelet-proekta
plan: "04"
subsystem: infra
tags: [github-actions, ci, ruff, mypy, pytest, coverage, postgres, redis]

requires:
  - phase: 01-fundament-vybor-steka-i-skelet-proekta/01-02
    provides: docker-compose стек (web/db/cache), entrypoint с exec "$@", pytest-инфраструктура
  - phase: 01-fundament-vybor-steka-i-skelet-proekta/01-03
    provides: зелёные ruff/mypy/pytest на скелете (cf30d5b), проверенные docker-first команды
provides:
  - .github/workflows/ci.yml — CI на каждый push/pull_request: один job check с поимёнными ступенями Lint → Typecheck → Migrations drift check → Tests (SC-3, D-06)
  - Постоянная защита SC-4 в CI: drift-check до pytest + тест-БД pytest-django из миграций на каждом прогоне
  - Локально доказанное зеркало всех четырёх CI-ступеней через docker compose run --rm web (те же команды дословно)
affects: [02-accounts, 03-catalog-geo, 04-listings, 05-media, 06-public-pages, 07-search, 08-messaging, 09-moderation]

actuals:
  tokens: 675        # chars/4 по реализованному diff (~2700 симв.: ci.yml 59 строк + AGENTS.md 1/1)
  tasks: 2
  commits: 1         # git rev-list --count 8d55dbc..9c00bbf (production; docs-коммиты SUMMARY вне счёта)
plan_head_before: 8d55dbc210f80da4a66311a698954cb3eb811f7a
plan_head_after: 9c00bbf4863c52ede31a40874d1e445f4915722a

tech-stack:
  added: []           # новых пакетов нет: CI ставит requirements/dev.txt с пинами 01-01 (T-01-SC); GitHub Actions — внешний сервис
  patterns:
    - "CI-ступень = отдельный именованный step GitHub Actions (не одна строка): падение краснит пайплайн поимённо (SC-3); seed для всех будущих workflow"
    - "Зеркалирование CI локально: каждая ступень workflow обязана проходить как docker compose run --rm web <та же команда> до пуша"
    - "Drift-check (makemigrations --check --dry-run) ставится ДО pytest — тихий дрейф моделей/миграций ловится раньше тестов (Pitfall 9)"

key-files:
  created:
    - .github/workflows/ci.yml
  modified:
    - AGENTS.md          # отклонение по правилу AGENTS.md: «No CI pipeline yet» перестал быть фактом

key-decisions:
  - "DJANGO_SETTINGS_MODULE=config.settings.test закреплён в job env CI: manage.py-ступень (drift-check) идёт через test-настройки с env-дефолтами localhost — тот же модуль, что pyproject задаёт для pytest (key_link плана)"
  - "pyproject.toml остался без правок: все четыре ступени зелёные на конфигах 01-01 — локальное зеркало не потребовало ни ослаблений, ни suppress'ов"
  - "Один job без matrix (Open Question №3 research'а RESOLVED): поимённость ступеней уже выполняет SC-3, matrix отложен до роста сьюта"

patterns-established:
  - "Workflow CI: triggers on [push, pull_request]; permissions contents: read; services postgres (health-cmd pg_isready, verbatim docs.github.com) + redis; pip-кэш от пинов == (cache-dependency-path requirements/*.txt)"
  - "CI-env = явные CI-значения, не секреты: DATABASE_URL/REDIS_URL на localhost сервисов, DJANGO_SECRET_KEY-заглушка (T-01-07)"

requirements-completed: [SC-3, SC-4]

coverage:
  - id: D1
    description: "Workflow .github/workflows/ci.yml: один job, четыре поимённые ступени, services postgres:18+redis:8, least-privilege permissions, pip-кэш"
    requirement: SC-3
    verification:
      - kind: other
        ref: "findstr-цепочка Task 1 (setup-python / postgres:18 / ruff / mypy / makemigrations / pytest / contents:) — все 7 гейтов exit 0"
        status: pass
      - kind: other
        ref: "key_links: requirements/dev.txt (pip install -r), pyproject (комментарий-ссылка на конфиги ступеней), config.settings.test (DJANGO_SETTINGS_MODULE в job env) — grep-паттерны найдены"
        status: pass
    human_judgment: false
  - id: D2
    description: "Зеркальный локальный прогон CI-ступеней в контейнере: ruff / mypy / drift-check / pytest — все exit 0; тест-БД из миграций против реальных db+cache"
    requirement: SC-4
    verification:
      - kind: integration
        ref: "docker compose run --rm web ruff check . → All checks passed!"
        status: pass
      - kind: integration
        ref: "docker compose run --rm web mypy . → Success: no issues found in 30 source files"
        status: pass
      - kind: integration
        ref: "docker compose run --rm web python manage.py makemigrations --check --dry-run → No changes detected"
        status: pass
      - kind: integration
        ref: "docker compose run --rm web pytest -v → 2 passed (tests/test_health.py: test_healthz_ok, test_home_counter_increments)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Фактический зелёный прогон job check на GitHub Actions при первом пуше ветки фазы"
    verification: []
    human_judgment: true
    rationale: "Внешний CI-сервис: первый прогон возможен только после пуша ветки (локально workflow неисполним); план явно относит фиксацию зелёности к /gsd-verify-work фазы (manual-verify по VALIDATION, RESEARCH § Environment Availability)"

duration: 6min
completed: 2026-11-18
status: complete
---

# Phase 1 Plan 4: CI-конвейер GitHub Actions Summary

**Workflow ci.yml: один job с поимёнными ступенями ruff → mypy → drift-check → pytest на services postgres:18+redis:8, зеркально доказанный локально в контейнере (4/4 ступени exit 0)**

## Performance

- **Duration:** 6 min
- **Started:** 18.11.2026T13:53:16 (локальное время сессии)
- **Completed:** 18.11.2026T13:58:48
- **Tasks:** 2
- **Files modified:** 2 (.github/workflows/ci.yml создан, AGENTS.md обновлён)

## Accomplishments

- Создан `.github/workflows/ci.yml` по verbatim-образцу RESEARCH 534–581: триггеры push/pull_request, permissions contents: read (T-01-07), job check на ubuntu-latest без matrix (Open Question №3)
- Четыре ступени качества — ОТДЕЛЬНЫЕ именованные steps: Lint (ruff check .), Typecheck (mypy .), Migrations drift check (makemigrations --check --dry-run, до pytest — Pitfall 9), Tests (coverage run -m pytest -v + coverage report) — падение любой краснит пайплайн поимённо (SC-3)
- Services: postgres:18 с health-опциями pg_isready (verbatim docs.github.com) и redis:8-alpine; env job — CI-значения без секретов + DJANGO_SETTINGS_MODULE=config.settings.test (test-настройки несут env-дефолты localhost)
- Все четыре CI-команды зеркально прогнаны локально через docker compose run --rm web: ruff «All checks passed!», mypy «no issues in 30 files», drift-check «No changes detected», pytest «2 passed» против живых db+cache — workflow не ссылается на неработающие команды
- pyproject.toml не потребовал правок: конфиги 01-01 выдержали первый полный прогон без suppress'ов

## Task Commits

Each task was committed atomically:

1. **Task 1: Workflow ci.yml — services + четыре ступени качества** - `9c00bbf` (feat)
2. **Task 2: Зеркальный локальный прогон CI-ступеней в контейнере** - без коммита: verify-only задача, изменений файлов не обнаружено (pyproject.toml правок не требовал; рабочее дерево чистое, кроме преждесуществующих untracked)

**Plan metadata:** см. итоговый docs-коммит SUMMARY/STATE/ROADMAP.

## Files Created/Modified

- `.github/workflows/ci.yml` - CI-пайплайн фазы: один job, services postgres:18+redis:8-alpine, ступени Install/Lint/Typecheck/Migrations drift check/Tests, pip-кэш от requirements/*.txt
- `AGENTS.md` - «No CI pipeline yet» заменён на проверенный факт о CI (правило same-commit обновления)

## Decisions Made

- DJANGO_SETTINGS_MODULE=config.settings.test закреплён в job env CI — manage.py-ступень drift-check идёт через test-настройки (env-дефолты localhost), тот же модуль, что pyproject задаёт для pytest; key_link «config.settings.test» выполнен явно
- В env нет реальных секретов: DJANGO_SECRET_KEY=ci-insecure-not-a-secret — явная CI-заглушка (T-01-07); комментарии ci.yml документируют verbatim-источники (setup-python README, docs.github.com)
- pyproject.toml не менялся: ступени зелёные на конфигах 01-01, подавлений не добавлено

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 / директива AGENTS.md] AGENTS.md обновлён тем же коммитом, что и ci.yml**
- **Found during:** Task 1 (создание workflow)
- **Issue:** AGENTS.md завершался утверждением «No CI pipeline yet» — с появлением workflow это перестаёт быть проверенным фактом; правило AGENTS.md требует обновлять файл тем же коммитом, что приносит tooling
- **Fix:** Фраза заменена на краткое описание CI (workflow, ступени, services, «first run happens on the first push of a branch»)
- **Files modified:** AGENTS.md
- **Verification:** commit 9c00bbf содержит оба файла; «Verified facts only» соблюдено — заявлено только существование/состав workflow, зелёность на GitHub не утверждается
- **Committed in:** 9c00bbf

---

**Total deviations:** 1 (документационная корректировка по директиве AGENTS.md; Rules 1–3 кодовых фиксов не потребовались)
**Impact on plan:** Нет scope creep; план исполнен как написан, отклонение — следствие явного правила репозитория.

## Issues Encountered

None

## Known Stubs

None - ci.yml функционален целиком; единственная незакрытая часть — фактический прогон на GitHub (внешний сервис, см. coverage D3 и Issues выше: отложено планом на /gsd-verify-work, не является стабом).

## User Setup Required

None - no external service configuration required. (CI-минуты GitHub Free-плана подтверждаются при первом прогоне — Open Question №2 research'а RESOLVED как runtime-проверка.)

## Next Phase Readiness

- Фаза 1 закрыта функционально: все 4 плана исполнены (SC-1…SC-4); следующая остановка — /gsd-verify-work фазы 1 (полный сьют + verify_bootstrap + визуальная фиксация зелёного CI-прогона на GitHub после пуша ветки)
- Все будущие фазы наследуют CI-гейт: каждый пуш проходит lint/typecheck/drift-check/tests; новые workflow строятся по ci.yml как seed (PATTERNS § Seed map)

## Self-Check: PASSED

- `.github/workflows/ci.yml` существует и закоммичен (git show 9c00bbf --stat: 2 files changed, create mode 100644) — FOUND
- Коммит задачи-предок HEAD: `git merge-base --is-ancestor 9c00bbf HEAD` — exit 0 — FOUND
- `evaluation-scope --plan 01-04 --commits-only --raw` → status: resolved, commits: [9c00bbf] (≥1 на этой ветке) — FOUND
- Леджер #3968: `git rev-list --count 8d55dbc..HEAD` = 1 — совпадает с `commits:` во frontmatter
- Повторно прогнанные acceptance criteria обоих задач и plan-level `<verification>` — все exit 0 (логи в coverage D1/D2)

*Phase: 01-fundament-vybor-steka-i-skelet-proekta*
*Completed: 2026-11-18*
