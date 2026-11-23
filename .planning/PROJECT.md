# Private Classifieds (Частные объявления)

## What This Is

Веб-сервис объявлений о продаже товаров и услуг **только для частных лиц**. Существующие площадки коммерциализированы: частные объявления теряются среди предложений компаний. Этот сервис решает обратную задачу — объявления частных продавцов остаются видимыми и не конкурируют с коммерческими предложениями.

## Core Value

Объявление частного лица находят покупателя — оно не тонет среди коммерческих предложений.

## Requirements

### Validated

(None yet — ship to validate)

### Active

Гипотезы до поставки (greenfield, источник — docs/PRD.md):

- [ ] Администратор ведёт иерархический рубрикатор товаров и услуг (создание/изменение дерева категорий)
- [ ] Администратор ведёт справочник городов
- [ ] Пользователь создаёт свои объявления
- [ ] Пользователь редактирует свои объявления
- [ ] Пользователь удаляет свои объявления
- [ ] Пользователь публикует свои объявления (не более 10 одновременно)
- [ ] Пользователь снимает свои объявления с публикации (объявление удаляется из БД)
- [ ] Пользователь ищет чужие объявления
- [ ] Пользователь читает свои сообщения
- [ ] Пользователь пишет сообщения продавцам и потенциальным покупателям
- [ ] Пользователь заполняет свой профиль (имя, телефон для связи, e-mail)

### Out of Scope

- Коммерческие аккаунты магазинов/компаний — концепция проекта прямо противоположна
- Платное продвижение и реклама объявлений — коммерциализация является проблемой, которую проект решает
- Мобильные приложения — в PRD не заявлены, web-first

## Context

- Единственный источник требований — `docs/PRD.md` (на русском).
- Greenfield-репозиторий: кода, манифестов и CI нет; стек намеренно не выбран.
- Обязательные поля объявления: ссылка на пользователя-продавца, город продажи, заголовок, описание товара/услуги, цена.
- Обязательные поля профиля: имя, телефон для связи, e-mail.
- Роли: администратор системы и пользователь.

## Constraints

- **Scale**: до 1 000 000 пользователей — архитектура должна проектироваться под нагрузку (PRD, НФТ)
- **Data**: снятие с публикации = удаление объявления из базы данных; архива/soft-delete для объявлений нет (PRD)
- **Limits**: заголовок ≤ 128 символов; описание ≤ 512 символов; сообщение ≤ 512 символов; ≤ 10 опубликованных объявлений на пользователя одновременно (PRD)
- **Tech stack**: закреплён ADR-0001 — Django 5.2 LTS + DRF, PostgreSQL 18, Redis 8, Python 3.13, gunicorn WSGI, WhiteNoise; Django Admin как админ-слой; SSR через Django-шаблоны (без SPA)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| GSD: granularity=fine, parallel execution, все агенты (research, plan check, verifier, drift guard), model_profile=inherit | Выбор пользователя при инициализации (auto-mode) | ✓ Принято |
| Стек: Django 5.2 LTS + DRF + PostgreSQL 18 + Redis 8, Python 3.13, gunicorn, WhiteNoise, Django Admin как админ-слой, SSR через Django-шаблоны | Явный выбор пользователя из вариантов A/B/C research (ADR-0001, user gate по правилу AGENTS.md) | ✓ Accepted — Phase 1 verified (22/22) |
| Горизонтальная перестройка ROADMAP: UX (дизайн, DESIGN.md) → UI (страницы на фикстурах) → бэкенд (прежние фазы 2–9) → запускная готовность | Решение пользователя (2026-11-23): весь UX/UI создаются раньше логики; mvp-маркер снимается с фаз 1–3 | — Pending (применить к ROADMAP первым шагом фазы 2) |
| Запрет Python-правок до фазы UI | Решение пользователя (2026-11-23): фаза UX — чистые документы; первые Python-изменения — стаб-view фазы UI | — Active |
| Ветвление: branching_strategy=phase (gsd/phase-{N}-{slug}) | Решение пользователя (2026-11-23) при переименовании рабочей ветки | ✓ Active |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-11-23 after Phase 1 (verified, transitioned; UX-first restructure pending)*
