---
phase: 01-fundament-vybor-steka-i-skelet-proekta
plan: "01"
subsystem: infra
tags: [adr, django, dependencies, pyproject, git-hygiene, supply-chain]

# Dependency graph
requires:
  - phase: 01-research/context
    provides: user stack decision D-01..D-08, verified dependency versions (PyPI resolution probe)
provides:
  - ADR-0001 fixing Variant B (Django 5.2 LTS + DRF, PostgreSQL 18, Redis 8) as the user's explicit choice (SC-1)
  - Pinned dependency manifests requirements/base.txt + requirements/dev.txt (14 packages, ==)
  - Single tooling config home pyproject.toml (pytest / ruff / mypy / django-stubs)
  - Secrets and CRLF hygiene (.gitignore, .gitattributes, .dockerignore, .env.example)
affects: [01-02-docker-skeleton, 01-04-ci-github-actions]

# Actuals (#2632) — pairs with the plan's estimate (22000 tokens, confidence: low)
actuals:
  tokens: 2265   # chars/4 over the 8 files actually created (9058 bytes of diff)
  tasks: 2
  commits: 2     # MEASURED: git rev-list --count d9c733f..HEAD

plan_head_before: d9c733fa96155efb0cec298b919e313f083f532f
plan_head_after: 6df56080d44ada811022a57e559af649f43900c9

# Tech tracking
tech-stack:
  added: ["Django==5.2.19", "djangorestframework==3.18.3", "gunicorn==27.0.1", "psycopg[binary]==3.3.9", "django-redis==7.0.0", "whitenoise==6.12.0", "django-environ==0.14.0", "pytest==9.2.0", "pytest-django==4.14.0", "ruff==0.17.5", "mypy==1.19.1", "django-stubs==5.2.9", "coverage==7.17.3", "factory_boy==3.3.3"]
  patterns: ["exact == pins for supply-chain control (updates = conscious commit)", "native TOML pytest config ([tool.pytest], pytest 9+)", "* text=auto eol=lf normalization on a Windows host"]

key-files:
  created:
    - docs/adr/0001-choice-of-stack.md
    - requirements/base.txt
    - requirements/dev.txt
    - pyproject.toml
    - .gitignore
    - .gitattributes
    - .dockerignore
    - .env.example
  modified: []

key-decisions:
  - "ADR-0001 records Variant B (Django 5.2 LTS + DRF, PostgreSQL 18, Redis 8) as the USER's explicit choice from A/B/C — SC-1 closed"
  - "All 14 dependencies pinned with ==; mypy held at 1.19.1 because django-stubs 5.2.9 declares compatible-mypy >=1.13,<1.20 (Pitfall 2)"
  - "ADR fixes Pitfall 1: dev DB of Phase 1 is disposable; custom User lands in Phase 2 BEFORE user data, with docker compose down -v volume reset"

patterns-established:
  - "ADR-series seed: docs/adr/NNNN-*.md, English section headers, Russian body"
  - "Single tooling home: pyproject.toml is the only place for tool configs"
  - "Secrets template pattern: .env.example with safe dev defaults only; .env gitignored from commit one"

requirements-completed: [SC-1]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "ADR-0001 in the repository fixing Variant B as the user's explicit stack choice, with alternatives and consequences (SC-1)"
    requirement: SC-1
    verification:
      - kind: other
        ref: "findstr /C:Decision, /C:Alternatives, /C:Consequences, /C:PostgreSQL, /C:Redis over docs/adr/0001-choice-of-stack.md — all exit 0"
        status: pass
    human_judgment: false
  - id: D2
    description: "Repository config foundation: 14 pinned dependencies (base+dev with -r base.txt inheritance), pyproject.toml tooling home, git/docker hygiene files"
    verification:
      - kind: other
        ref: "8-check findstr chain over requirements/base.txt (Django==5.2.19), requirements/dev.txt (mypy==1.19.1, '-r base.txt'), pyproject.toml ([tool.pytest]), .gitattributes (eol=lf), .env.example (DJANGO_SECRET_KEY), .gitignore (__pycache__), .dockerignore (.planning) — all exit 0"
        status: pass
    human_judgment: false

# Metrics
duration: 6 min
completed: 2026-11-18
status: complete
---

# Phase 1 Plan 01: Выбор стека (ADR-0001) и конфиг-фундамент Summary

**ADR-0001 фиксирует Вариант B (Django 5.2 LTS + DRF, PostgreSQL 18, Redis 8) как явный выбор пользователя; 14 зависимостей запинены `==` (mypy 1.19.1), pyproject.toml — единый дом тулинга, секреты вне git, eol=lf против CRLF**

## Performance

- **Duration:** ~6 min
- **Started:** 18 ноября 2026 12:27 (local)
- **Completed:** 18 ноября 2026 12:33 (local)
- **Tasks:** 2 / 2
- **Files created:** 8

## Accomplishments

- **SC-1 закрыт:** `docs/adr/0001-choice-of-stack.md` (Accepted) фиксирует Вариант B как решение пользователя из вариантов A/B/C research'а, с D-01…D-08, отклонёнными альтернативами A/C и последствиями (одноразовая dev-БД до Phase 2, пин mypy 1.19)
- Зависимости запинены точно (`==`) в `requirements/base.txt` (7 рантайм) и `requirements/dev.txt` (`-r base.txt` + 7 dev) — supply-chain контроль (T-01-02/T-01-SC), включительно с `mypy==1.19.1` внутри диапазона django-stubs 5.2.9 (Pitfall 2)
- `pyproject.toml` — единый дом конфигов: `[tool.pytest]` (native TOML, pytest 9+) с `DJANGO_SETTINGS_MODULE = "config.settings.test"`, `[tool.ruff] target-version = "py313"`, `[tool.mypy]` с django-stubs-плагином (non-strict, D-06), `[tool.django-stubs]`
- Git/build-гигиена: `.env` в `.gitignore` (T-01-01), `.env.example` только с dev-дефолтами, `.gitattributes` с `* text=auto eol=lf` (Pitfall 5 — защита будущего entrypoint.sh), `.dockerignore` отсекает `.env`/`.planning`/`.opencode`/`docs` от build-контекста

## Task Commits

Each task was committed atomically:

1. **Task 1: ADR-0001 — зафиксировать выбор стека пользователя** - `ae2614c` (docs)
2. **Task 2: Конфиги репозитория — пины, pyproject, git-гигиена** - `6df5608` (chore)

## Files Created/Modified

- `docs/adr/0001-choice-of-stack.md` - ADR выбора стека (SC-1): Status/Context/Decision/Alternatives/Consequences
- `requirements/base.txt` - 7 рантайм-пинов (Django 5.2.19 … django-environ 0.14.0)
- `requirements/dev.txt` - `-r base.txt` + 7 dev-пинов (pytest … factory_boy)
- `pyproject.toml` - конфиги pytest/ruff/mypy/django-stubs
- `.gitignore` - .env, кэши тулинга, staticfiles, .venv
- `.gitattributes` - нормализация концов строк в LF
- `.env.example` - 7 переменных окружения с безопасными dev-дефолтами
- `.dockerignore` - exclusions для build-контекста Docker

## Decisions Made

- Перенос D-01…D-08 в ADR дословно (формулировки CONTEXT.md, без переизобретения) — включая явную фиксацию «выбор сделал пользователь» (критерий SC-1)
- Пин `mypy==1.19.1` зафиксирован и в requirements, и текстом в Consequences ADR (django-stubs 5.2.9: `compatible-mypy: mypy>=1.13,<1.20`)
- Содержимое 7 конфиг-файлов — строго перечисленный в плане набор (никаких extras): фундамент расширяется позже

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Опечатка в тексте ADR**
- **Found during:** Task 1 (до верификации)
- **Issue:** «кастонной» вместо «кастомной» в секции Consequences
- **Fix:** исправлено Edit'ом до прогона findstr-гейта
- **Files modified:** docs/adr/0001-choice-of-stack.md
- **Verification:** findstr-гейт задачи 1 зелёный (exit 0)
- **Committed in:** ae2614c

---

**Total deviations:** 1 auto-fixed (опечатка, исправлена до коммита).
**Impact on plan:** отсутствует — план исполнен как написан.

## Issues Encountered

- **cmd-quoting на хосте:** кавычки передаются буквально в argv, поэтому verify-литерал `"-r base.txt"` (пробел + ведущий дефис) исполнен через временный `.cmd`-файл, парсимый cmd.exe нативно — семантика verify-команды сохранена точно, все 8 проверок exit 0. Адаптация окружения, не отклонение от плана.
- **Untracked-артефакты тулинга оставлены как есть** (вне scope, scope boundary): `.idea/`, `.planning/research/.cache/`, `.planning/state.json`, `.opencode/rules/git-new-files.md` (последний — «правило на диске», помечено так в PATTERNS.md). Содержимое `.gitignore` ограничено списком из плана.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Готов фундамент для **01-02**: Dockerfile (`COPY requirements/` → `pip install -r requirements/base.txt`), compose с переменными из `.env.example`
- Готов фундамент для **01-04**: CI (`pip install -r requirements/dev.txt`, конфиги ruff/mypy/pytest уже в `pyproject.toml`)
- Осознанная ссылка вперёд: `pyproject.toml` указывает на `config.settings.test` — файл настроек создаёт план 01-02 (key_link из must_haves)
- Блокеров нет; AGENTS.md-обновление (реальные команды тулинга) — план 01-03, как и заложено

## Self-Check: PASSED

- Все 8 созданных файлов существуют на диске (`dir /b` — 8/8 FOUND)
- Оба task-коммита — предки HEAD (`git merge-base --is-ancestor ae2614c/6df5608 HEAD` — OK)
- commits = 2 измерено из ledger (`git rev-list --count d9c733f..HEAD`), не рассказано
- Оба findstr-гейта задач и plan-level verification зелёные; `.env` в git status отсутствует

---
*Phase: 01-fundament-vybor-steka-i-skelet-proekta*
*Completed: 2026-11-18*
