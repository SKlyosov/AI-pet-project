---
phase: "1"
slug: "fundament-vybor-steka-i-skelet-proekta"
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: "2026-11-23"
---

# Phase 1 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Хост ↔ compose-сеть | Порты db/cache опубликованы только на 127.0.0.1 хоста; доступ извне машины невозможен | SQL/Redis-трафик, dev-пароль из .env |
| Разработчик ↔ git-репозиторий | Секреты живут только в .env (gitignored); в репозитории — имена переменных и dev-дефолты | .env.example (без секретов) |
| GitHub ↔ CI-раннер | Workflow с least-privilege permissions; CI-env — явные незасекреченные заглушки | Исходники, requirements-пины |
| Браузер ↔ web (gunicorn) | Единственная публичная точка фазы — / и /healthz; отдают минимум метаданных | JSON статуса, HTML счётчика |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T-01-01 | Information Disclosure | .gitignore / .env.example | high | mitigate | `.gitignore:1` — `.env`; `.env.example` содержит только имена+dev-дефолты (grep-проверено 2026-11-23) | closed |
| T-01-02 | Tampering | requirements/*.txt (supply chain PyPI) | medium | mitigate | Точные пины `==` всех 14 пакетов (base.txt/dev.txt; VERIFICATION 22/22 подтверждает гейты) | closed |
| T-01-SC | Tampering | pip-установки (PyPI) | high | mitigate | Пины `==` + Package Legitimacy Audit в RESEARCH (все Approved); после 01-01 новых пакетов не добавлялось (git-история: только режим manage.py и настройки тестов) | closed |
| T-01-03 | Information Disclosure | apps/core/views.py healthz | low | mitigate | Ответ только `{"status", "checks"}` без версий/хостов/DSN — поведенчески проверено 2026-11-23 в обеих ветках (200 ok / 503 fail) | closed |
| T-01-04 | Elevation | compose.yaml (порты db/cache) | medium | mitigate | `compose.yaml:15,29` — `127.0.0.1:15432:5432`, `127.0.0.1:16379:6379` (loopback-only); `compose.yaml:7` — `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set in .env}` (обязателен) | closed |
| T-01-05 | Information Disclosure | config/settings (DEBUG) | high | mitigate | `base.py:18` — `DEBUG = False` (безопасный дефолт) и `prod.py:9` — `DEBUG = False`; `manage.py check` под prod зелёный (VERIFICATION) | closed |
| T-01-06 | Spoofing | config/settings/prod.py ALLOWED_HOSTS | medium | mitigate | `prod.py:15` — `DJANGO_ALLOWED_HOSTS` из env, явный список; в base — `ALLOWED_HOSTS: []` (запирающий дефолт); звёздочки нет | closed |
| T-01-07 | Elevation / Tampering | .github/workflows/ci.yml | low | mitigate | `ci.yml:8-9` — `permissions: contents: read`; секретов нет (`DJANGO_SECRET_KEY` — явная CI-заглушка) | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|

*Accepted risks do not resurface in future audit runs.*

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-11-23 | 8 | 8 | 0 | orchestrator (L1 grep-depth + behavioral evidence; short-circuit per asvs_level 1, register_authored_at_plan_time) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-11-23
