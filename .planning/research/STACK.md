# Stack Research

**Domain:** Private classifieds web marketplace (частные объявления, web-first)
**Researched:** 2026-11-18
**Confidence:** HIGH (версии проверены по живым реестрам/официальным сайтам 18.11.2026; MEDIUM только для обзорных заявлений о стеках компаний — см. Sources)

> **Правило репозитория (AGENTS.md):** язык/фреймворк не выбирается без явного согласия пользователя. Документ даёт **одну основную рекомендацию (Вариант A)** и **две жизнеспособные альтернативы из других экосистем (B, C)** с явными tradeoffs. Финальный выбор — за пользователем на фазе 1 планирования.

## Recommended Stack

### Core Technologies

**Вариант A (основная рекомендация): TypeScript-монолит «NestJS + Next.js + PostgreSQL»**

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Node.js | 26 LTS (26.13.1; допустимо 24 LTS — 24.22.3) | Среда исполнения бэкенда | Active LTS до окт. 2027, security до апр. 2029. На хосте разработчика уже стоит Node 24.21 — совместимо со всем списком ниже. Один язык на фронт и бэк ускоряет итерации небольшой команды/агентов. |
| NestJS | 12 (12.5.1, @nestjs/core) | Бэкенд-фреймворк (модульный монолит) | Стандарт де-факто для структурированных Node-бэкендов: модули, DI,内置 guards/pipes/interceptors, встроенная поддержка WebSocket-гейтвеев и микросервисов (путь роста без смены каркаса). Работает поверх Express или Fastify. Конвенции фреймворка особенно ценны при генерации code агентами. |
| TypeScript | 7.0 (7.0.2) | Язык | Текущий мажор (нативный компилятор — быстрый typecheck). Если отдельные инструменты тулчейна ещё не поддержали 7.x — откат на предыдущую стабильную ветку 5.9/6.x без измененияcode. |
| PostgreSQL | 18 (18.7) | Единственная основная БД: пользователи, объявления, рубрикатор, города, сообщения | Latest GA (PG 19 — только RC2, не для прода). Данные строго реляционные: иерархический рубрикатор (self-FK / ltree), справочник городов, FK «объявление→продавец/город/категория». Лимиты PRD ложатся в типы: `varchar(128)` заголовок, `varchar(512)` описание/сообщение; «≤10 опубликованных» — частичный уникальный индекс `CREATE UNIQUE INDEX ... ON listings(user_id) WHERE status='published'` c лимитом через констрейнт-триггер или проверку в транзакции; «снятие с публикации = удаление» — обычный `DELETE`, без soft-delete. Масштаб: ≤10 млн строк × ~0.7 КБ = единицы ГБ + индексы — комфортно для одного инстанса, реплика read-only на вырост. |
| Prisma | 7 (7.10.1, prisma + @prisma/client) | ORM + миграции | Типобезопасные запросы и декларативные миграции (`prisma migrate`) для команды, которая хочет конвенцию, а не ручной SQL. Prisma 7 — TS-клиент без Rust-движка в рантайме. Если нужен SQL-контроль/edge — см. Drizzle в Supporting. |
| Next.js | 16 (16.4.6) | Фронтенд (SSR/ISR) + страницы объявлений | Объявления живут на органическом поиске (SEO обязателен): SSR/ISR для страниц объявлений и категорий из коробки, App Router, RSC. Админка (рубрикатор, города) — те же Next.js-роуты. React 19 в peer-deps. |
| React | 19 | UI-рантайм | Единственная поддерживаемая мажор-линия Next.js 16 (peer: ^18.2 \|\| ^19 — берём 19). |
| Redis | 8.10 (8.10.3; или Valkey 8 — BSD-форк) | Сессии, кэш справочников, rate-limit, очередь | Три-лицензия RSALv2/SSPLv1/**AGPLv3** с версии 8.0 — AGPL-опция снимает вопрос «не-OSI» для использования как внутренний кэш/брокер. Для проекта это отдельный сервер (не распространяется), лицензия не триггерится. Если политика требует BSD — Valkey 8, клиенты (ioredis) совместимы. Кэшировать рубрикатор и справочник городов (админские справочники читаются на каждый запрос поиска), хранить сессии. |
| PostgreSQL FTS (russian config) | встроено в PG 18 | Поиск объявлений на старте | Встроенная конфигурация `russian` (стеммер + стоп-слова), `websearch_to_tsquery`, GIN-индекс по `to_tsvector('russian', title \|\| ' ' \|\| description)`. При ≤10 млн коротких документов (128+512 символов) этого достаточно; ноль дополнительной инфраструктуры. |
| Zod | 4 (4.6.7) | Валидация входа | Единая схема валидации лимитов PRD (128/512/≤10) на API-границе и в формах; типы выводятся автоматически. |

**Масштаб до 1 000 000 пользователей — оценка:** 1 млн зарегистрированных ≠ 1 млн одновременно активных. При ≤10 опубликованных объявлений на пользователя и коротких текстах это маленькая БД (≤10 млн строк) и типично десятки–сотни RPS. Монолит (NestJS) + один PostgreSQL 18 (+read-реплика на вырост) + Redis закрывает НФТ с запасом; горизонтальное масштабирование — реплики приложения за балансировщиком, без микросервисов.

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| drizzle-orm | 0.45.4 | Лёгкий SQL-ориентированный ORM | Вместо Prisma, если команда предпочитает SQL-подобный API и минимальную codegen-магию (в т.ч. edge-рантаймы). Не смешивать с Prisma в одном проекте. |
| @nestjs/config | 4.3.5 | Типизированная конфигурация (.env) | Всегда в варианте A. |
| Socket.IO | 4.8.4 | real-time доставка сообщений | Этап 2 обмена сообщениями: сначала REST + short-polling (сообщения ≤512 символов), Socket.IO-гейтвей NestJS — когда нужна «живая» доставка/статусы. Rooms = диалог между продавцом и покупателем. |
| ioredis | 6.0.0 | Redis-клиент | Кэш/сессии/rate-limit в варианте A. |
| pg | 8.23.1 | Нативный драйвер PG | Raw-SQL для FTS-запросов и частичных индексов рядом с Prisma. |
| BullMQ | 6.7.7 | Фоновые задачи (очередь на Redis) | Отложенные уведомления e-mail,批量 переиндексация при переходе на Meilisearch. Не нужен в первом срезе. |
| Pino | 10.4.0 | Структурные логи | Всегда; JSON-логи + requestId. |
| Tailwind CSS | 4.3.5 | Стизация UI и админки | Всегда в варианте A (быстрый консистентный UI без дизайн-системы с нуля). |
| Meilisearch | 1.57.0 | Отдельный поисковый движок | Когда PG FTS перестанет хватать: typo-tolerance, фейсеты по категориям/городам/цене, ранжирование. Кириллица поддерживается (charabia). Есть windows-бинарь и Docker-образ. Индекс синхронизировать из БД (BullMQ/флип при публикации). |
| class-validator | 0.15.1 | Декораторная валидация DTO | Только если выбран стиль NestJS-DTO вместо Zod; не смешивать с Zod. |
| Vitest | 5.1.0 | Unit/интеграционные тесты | Всегда (юнит-тесты лимитов и счётчика публикаций). |
| Playwright | 1.65.1 (@playwright/test) | E2E | Сценарии «создать→опубликовать→снять с публикации→строка удалена». |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Docker + Docker Compose | Локальная среда: postgres:18, redis:8.x (или valkey), meilisearch:v1.57 | Windows-хост: приложения нативно, инфраструктуру в контейнерах. |
| ESLint + Prettier | Единый стиль | flat config; eslint 9.x. |
| pnpm | Пакетный менеджер | Быстрый, строгий; альтернатива npm — на вкус команды. |
| pgAdmin / DBeaver | Работа с БД | Проверка «unpublish = строка удалена» руками на UAT. |
| Caddy или Nginx | Реверс-прокси/terimination TLS | Caddy проще (авто-HTTPS); Nginx — если привычнее. |
| GitHub Actions | CI | lint + typecheck + vitest + playwrightmatrix на PR. |

## Installation

```bash
# Core (вариант A)
npm install @nestjs/core@^12 @nestjs/common@^12 @nestjs/config@^4 next@^16 react@^19 react-dom@^19
npm install prisma@^7 @prisma/client@^7 zod@^4 ioredis@^6 pg@^8 pino@^10
npm install socket.io@^4 @nestjs/websockets@^12 @nestjs/platform-socket.io@^12  # этап 2
npm install bullmq@^6                                                  # фоновые задачи
npm install -D typescript@^7 vitest@^5 @playwright/test@^1.65 tailwindcss@^4 eslint@^9 prettier
```

```bash
# Инфраструктура (docker-compose.yml services)
#   db:    postgres:18-alpine        (POSTGRES_DB=classifieds)
#   cache: redis:8-alpine | valkey/valkey:8-alpine
#   search: getmeili/meilisearch:v1.57   (только когда перерастаем PG FTS)
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Вариант A: NestJS 12 + Next.js 16 + PostgreSQL 18 (TypeScript) | **Вариант B: Python/Django 5.2 LTS + DRF + PostgreSQL 18** | Если максимальная ценность — **Django Admin из коробки**: рубрикатор и справочник городов — это две админ-CRUD-сущности PRD, Django отдаёт их почти бесплатно. Плюс: зрелые batteries (auth, forms, ORM+миграции), LTS до апр. 2028, Python 3.12–3.14. Минусы: два языка при SSR-фронте на Next.js (либо Templates+htmx — тогда SPA-мессенджер сложнее), raw-производительность ниже Node/JVM (при наших RPS — не блокер), real-time требует Django Channels (ASGI-стек). Поисковый/кэшевой контур тот же: PG FTS → Meilisearch, Redis. |
| Вариант A: NestJS 12 + Next.js 16 + PostgreSQL 18 (TypeScript) | **Вариант C: JVM — Kotlin + Spring Boot 4.1 (4.1.2) + Spring Data JPA + PostgreSQL 18, JDK 25/27 LTS** | Если приоритет — максимальная пропускная способность на инстанс, корпоративная наблюдаемость (Actuator/Micrometer) и команда знает JVM. Spring Boot 4.1 вышел в 2026 (Spring Framework 7.0.x, Hibernate 7.4, поддержка Java 27 LTS). Минусы: больше шаблонного code и медленнее итерации для малой команды; фронт всё равно отдельный (Next.js или Thymeleaf); для домена с жёсткими лимитами и малыми данными преимущество JVM не реализуется. |
| Вариант A: NestJS 12 + Next.js 16 + PostgreSQL 18 (TypeScript) | Вариант D (упомянут для полноты): Go (chi/echo) + sqlc | Если нужна минимальная latency при минимальных ресурсах. Минус: нет аналога Django-admin/NestJS-конвенций — всю админку и валидацию строить руками; для этого проекта time-to-market хуже. |
| PostgreSQL FTS (russian) | Meilisearch 1.57 | Когда нужны typo-tolerance, фейсеты, «похожие объявления» — раньше, чем PG FTS это даст. |
| Redis 8.10 | Valkey 8 | Если политика лицензий требует BSD (клиенты и протокол совместимы). |
| Prisma 7 | Drizzle ORM 0.45.4 | SQL-first команда, edge-рантаймы, неприязнь к codegen. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| MongoDB как основная БД | Данные строго реляционные (дерево рубрикатора, FK города/продавца, транзакционная публикация с лимитом ≤10); слабее FTS для русского; теряем констрейнты целостности | PostgreSQL 18 |
| Микросервисы + Kubernetes с первого дня | 1 млн зарегистрированных при жёстких лимитах данных = маленькая БД и умеренные RPS; микросервисы умножат эксплуатационную сложность и замедлят поставку. Все крупные маркетплейсы стартовали монолитом | Модульный монолит (NestJS modules / Django apps) + read-реплика PG на вырост |
| Elasticsearch/OpenSearch с первого дня | JVM-кластер ради ≤10 млн коротких документов — неоправданная эксплуатация; PG FTS покрывает старт, Meilisearch — середину | PG FTS → Meilisearch 1.57 (OpenSearch — только настоящий большой масштаб фейсетов) |
| «Голый» Express без структуры | Нет модульности/DI/конвенций — долг монументализируется быстро; NestJS 12 использует тот же Express/Fastify под капотом, не теряя производительности | NestJS 12 |
| Soft-delete (`deleted_at`) для объявлений | Прямо противоречит PRD: снятие с публикации = **удаление строки из БД**. Архив/черновики объявлений в PRD нет | `DELETE` + каскадная очистка зависимостей (сообщения живут отдельно, но ссылки на объявление — по FK ON DELETE) |
| GraphQL | Фиксированный набор сценариев (PRD), SSR-фронт; GraphQL добавляет слой и сложность кэширования без выгоды | REST (NestJS) / SSR-запросы |
| PHP/Laravel | Жизнеспособно (классика жанра — Leboncoin), но при greenfield-старте и SSR-фронте на React не даёт преимуществ перед A/B, а разброс языков (PHP+JS) увеличивает контекст для агентов/новых разработчиков | Вариант A или B |
| Свои SMS-шлюзы/своё хранилище файлов | Профиль обязателен по PRD (имя/телефон/e-mail), но верификация SMS и файлы в PRD не входят; строить своё — трата фаз | Внешний SMS-API/S3-совместимое хранилище, если потребность появится |

## Stack Patterns by Variant

**Если SEO — главный канал трафика (объявления должны находиться в поисковиках):**
- Next.js 16 SSR/ISR для страниц объявлений и категорий, `sitemap.xml`, канонические URL город×категория
- Потому что organic-трафик — стандартный источник покупателей для объявлений; SPA-без-SSR убивает индексацию

**Если появятся фотографии объявлений (в PRD их нет):**
- S3-совместимое хранищество (MinIO self-hosted / облачное) + CDN, картинки через отдельный сервис-ресайзер
- Потому что хранить блобы в PostgreSQL — анти-паттерн

**Если устойчиво >100–200 RPS поиска или нужны фейсеты/опечатки:**
- Вынести поиск в Meilisearch 1.57, синхронизация индекса при publish/unpublish (unpublish = `DELETE` в индексе тоже)
- Потому что PG FTS не даёт typo-tolerance и фасетного ранжирования из коробки

**Если нужен real-time мессенджер «как в мессенджерах» (статусы доставки, online):**
- Socket.IO-гейтвей NestJS (rooms на диалог) поверх REST-истории сообщений
- Потому что SSE — только сервер→клиент, а polling не даёт UX; но на старте polling дешевле

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| @nestjs/core@12.5.1 | Node >= 20 | engines: `>=20`; работает на Node 24 LTS и 26 LTS |
| next@16.4.6 | Node >= 20.9; React 18.2/19 | peer `react ^18.2 \|\| ^19`; RSC требуют React 19 |
| prisma@7.10.1 | Node ^20.19 \|\| ^22.12 \|\| >=24; PostgreSQL 18 | Проверить матрицу поддерживаемых PG-мажоров при сборке (Prisa поддерживает актуальные мажоры PG) |
| socket.io@4.8.4 | @nestjs/websockets@12 (ws-адаптер) | Комбинация стандартная, документирована NestJS |
| zod@4.6.7 | class-validator НЕ смешивать | Выбрать один механизм валидации на проект |
| Meilisearch v1.57 | Docker `getmeili/meilisearch:v1.57`; windows-amd64 binary | Master-key обязателен в прод |
| Django 6.1 (вариант B) | Python 3.12–3.15 | Для 5.2 LTS — Python 3.10–3.14 |
| Spring Boot 4.1.2 (вариант C) | JDK 17+ (runtime до Java 27 LTS включительно), Hibernate 7.4, Tomcat 11 | Spring Framework 7.0.x в комплекте |

## Sources

- endoflife.date/nodejs (обновлено 2026-11-12) — Node 26 Active LTS / 24 maintenance; HIGH
- postgresql.org/support/versioning/ + новость 2026-11-12 «PostgreSQL 18.7 … and 19 RC 2 Released» — PG 18.7 GA, PG 19 не-GA; HIGH
- registry.npmjs.org/@nestjs/core/latest, /next/latest, /@prisma/client/latest (получено 2026-11-18) — NestJS 12.5.1, Next 16.4.6, Prisma 7.10.1 + engines; HIGH
- npm view (2026-11-18): drizzle-orm 0.45.4, socket.io 4.8.4, zod 4.6.7, typescript 7.0.2, vitest 5.1.0, @playwright/test 1.65.1, pino 10.4.0, ioredis 6.0.0, pg 8.23.1, bullmq 6.7.7, tailwindcss 4.3.5, class-validator 0.15.1; HIGH
- endoflife.date/django (обновлено 04.11.2026) — Django 6.1.3 / 5.2 LTS; HIGH
- endoflife.date/redis (обновлено 27.10.2026) — Redis 8.10.3, три-лицензия с 8.0 (AGPLv3-опция); HIGH
- api.github.com/repos/spring-projects/spring-boot/releases/latest — Spring Boot v4.1.2 (Spring Framework 7.0.10, поддержка Java 27); HIGH
- api.github.com/repos/meilisearch/meilisearch/releases/latest — Meilisearch v1.57.0 (опубликовано 2026-11-16); HIGH
- PostgreSQL docs: Full Text Search (конфигурация `russian`, `websearch_to_tsquery`, GIN) — postgresql.org/docs/18/textsearch.html; HIGH (функциональность стабильна годами)
- Стеки крупных маркетплейсов (Avito: Go/Kotlin/Tarantool/ClickHouse; Vinted: Rails-монолит; OLX: PHP+Go; Leboncoin: PHP/Symfony; Wallapop: Django исторически) — **MEDIUM, по training-данным, живой fetch был недоступен (WebSearch 403)**; использовано только как аргумент «монолит → микросервисы по мере роста», не как версия пакета
- Websearch-провайдеры (встроенный WebSearch → HTTP 403; BRAVE_API_KEY не задан) — исследование выполнено прямыми WebFetch запросами к первоисточникам выше

---
*Stack research for: private classifieds marketplace (до 1 000 000 пользователей)*
*Researched: 2026-11-18*
