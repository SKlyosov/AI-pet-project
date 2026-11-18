# Architecture Research

**Domain:** Веб-маркетплейс частных объявлений (classifieds, private-only)
**Researched:** 2026-11-18
**Confidence:** MEDIUM

> Оценка честно: по иерархии источников (classify-confidence) провайдеры websearch/webfetch дают тир LOW. Общая оценка MEDIUM обоснована перекрёстным подтверждением: ядро выводов сходится у 3+ независимых источников (практикующие инженеры, официальная документация PostgreSQL, comparison-гайды). Одиночные некросс-проверенные тезисы помечены LOW по ходу текста.

## Standard Architecture

### System Overview

Единственный исследовательский консенсус для нового маркетплейса: **модульный монолит + одна реляционная БД**, с заранее спроектированными швами для будущего выделения поискового движка и realtime-транспорта сообщений. Микросервисы с первого дня — анти-паттерн для greenfield-маркетплейса (Fowler «Monolith First» и ряд гайдов 2025–2026 сходятся: сначала монолит, выделение сервисов — по фактическим bottleneck'ам).

```
┌──────────────────────────────────────────────────────────────────┐
│                    Client Layer (web, SSR-first)                 │
├────────────────┬────────────────┬────────────────┬───────────────┤
│  Public Site   │  Account Pages │  Admin Console │               │
│  (search/list/ │  (my listings, │  (categories,  │               │
│   ad detail)   │   messages)    │   cities)      │               │
└───────┬────────┴────────┬───────┴────────┬───────┴───────────────┘
        │                 │                │
┌───────┴─────────────────┴────────────────┴───────────────────────┐
│              Application Layer — Modular Monolith                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Identity │ │ Catalog  │ │  Geo     │ │ Listings │ │ Search │ │
│  │ &Profile │ │ (tree)   │ │ (cities) │ │ (+quota) │ │ (read) │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └───┬────┘ │
│  ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐ ┌────┴─────┐      │      │
│  │Messaging │ │  Admin   │ │(outbox → │ │ Indexer  │──────┘      │
│  │          │ │  policy  │ │ indexer) │ │ (later)  │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
├──────────────────────────────────────────────────────────────────┤
│                        Data Layer                                 │
│  ┌────────────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ RDBMS (PostgreSQL) │  │ Search index  │  │ Cache (later)   │  │
│  │ users, categories, │  │ Phase 1: FTS  │  │ reference data: │  │
│  │ cities, listings,  │  │ Phase 2:      │  │ categories,     │  │
│  │ conversations,     │  │ Meilisearch/  │  │ cities, unread  │  │
│  │ messages, quota    │  │ Typesense     │  │ counts          │  │
│  └────────────────────┘  └───────────────┘  └─────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Identity & Profile | Регистрация, аутентификация, профиль (имя, телефон, e-mail — обязательные поля PRD) | Session-based auth в монолите; таблица `users` |
| Catalog (категории) | Иерархический рубрикатор, CRUD администратора, валидация ссылок объявлений на листовой узел | Adjacency list (`parent_id`) + recursive CTE; денормализованный `path` для фильтра поддерева в поиске |
| Geo (города) | Справочник городов, CRUD администратора, привязка объявления к городу | Плоская справочная таблица `cities`; кэшируется целиком — маленькая и редко меняется |
| Listings | Жизненный цикл объявления: черновик → опубликовано; редактирование; удаление; **снятие с публикации = hard DELETE**; квота ≤10 активных | Модуль с транзакционной публикацией; квота — счётчик на пользователя с CHECK-ограничением |
| Search | Поиск чужих объявлений: текст, фильтры (поддерево категорий, город, цена), сортировка, пагинация | Phase 1: Postgres FTS (`tsvector` + GIN) + btree-фильтры; Phase 2 (по нагрузке): Meilisearch/Typesense через indexer + outbox |
| Messaging | Диалоги, привязанные к объявлению; сообщения ≤512 символов; непрочитанные | Таблицы `conversations` + `messages`; транспорт Phase 1 — HTTP (polling при обновлении страницы), апгрейд — SSE/WebSocket |
| Admin Console | Управление рубрикатором и городами; контроль ссылочной целостности справочников | Те же модули Catalog/Geo с admin-политиками; RESTRICT на удаление используемых записей |
| Indexer / Outbox | (Позже) Надёжная синхронизация БД → поисковый индекс при создании/удалении объявлений | Transactional outbox таблица + воркер; не нужен, пока поиск живёт в Postgres |

## Recommended Project Structure

Стек не выбран (правило AGENTS.md) — раскладка даётся модульно, вне конкретного фреймворка; она одинаково ложится на NestJS-модули, Django apps, Spring modules, Go packages.

```
src/
├── modules/
│   ├── identity/          # регистрация, auth, профиль
│   │   ├── domain/        # сущности, политики (обязательность полей)
│   │   └── api/           # HTTP-эндпоинты
│   ├── catalog/           # дерево категорий (admin CRUD + валидация ссылок)
│   ├── geo/               # справочник городов (admin CRUD)
│   ├── listings/          # lifecycle, квота, unpublish=hard delete
│   │   ├── domain/        # state machine: draft -> published; квота
│   │   ├── api/           # CRUD + publish/unpublish
│   │   └── search/        # СПЕЦИФИЧНО: только модуль listings пишет в индекс
│   ├── search/            # read-side: запросы пользователя, ранжирование
│   │   └── index/         # интерфейс SearchIndex (Postgres FTS | Meili | ...)
│   └── messaging/         # диалоги, сообщения, непрочитанные
├── shared/                # БД-миграции, общие типы, инфраструктура
│   ├── db/
│   └── contracts/         # межмодульные интерфейсы (не прямые импорты внутренностей)
└── app/                   # сборка приложения, роутинг, middleware
```

### Structure Rationale

- **modules/:** границы по бизнес-возможностям (bounded context'ам), а не по техническим слоям — это и есть «модульный» монолит; каждый модуль владеет своими таблицами, чужие таблицы читаются только через контракт модуля.
- **listings/search внутри listings, read-side отдельно:** запись в индекс — ответственность владельца данных (listings); чтение/ранжирование — отдельный read-side модуль `search`, которому всё равно, где физически индекс (FTS или внешний движок). Это шов для будущего выделения поискового сервиса без переписывания.
- **shared/db:** миграции в одном месте гарантируют порядок развёртывания схемы (справочники → listings → messaging).

## Architectural Patterns

### Pattern 1: Modular Monolith with module-owned data

**What:** Один деплоймент, одна БД, но каждый модуль сессионно владеет своими таблицами; межмодульный доступ — только через публичный контракт (интерфейс/сервис), не через чужие таблицы.
**When to use:** Greenfield-маркетплейс до сотен тысяч пользователей; переход к микросервисам — только при доказанных bottleneck'ах или нескольких командах.
**Trade-offs:** Плюсы — локальная отладка, одна транзакция на операцию (квота + объявление + индекс атомарны в Postgres-фазе), дешёвый ops. Минусы — требует дисциплины границ; при её отсутствии вырождается в «большой ком грязи».

**Example:**
```typescript
// shared/contracts/listings.ts — единственное окно в модуль listings
export interface ListingService {
  publish(input: PublishListing): Promise<ListingId | QuotaExceeded>;
  unpublish(id: ListingId, actor: UserId): Promise<void>; // hard delete
  countActive(owner: UserId): Promise<number>;
}
// модуль messaging НЕ знает про таблицу listings — только про этот контракт
```

### Pattern 2: DB-arbitrated quota (≤10 активных объявлений)

**What:** Лимит «не более 10 одновременно опубликованных» проверяет база, а не приложение: инкремент счётчика и вставка/статус-переход объявления — одна транзакция; конкуренция двух одновременных публикаций сериализуется блокировкой строки счётчика.
**When to use:** Всегда для per-user капов; проверка в приложении (`SELECT count(*)` без блокировки) даёт гонку, при которой два параллельных запроса проходят проверку и лимит превышается.
**Trade-offs:** Счётчик — денормализация, которую надо поддерживать при каждом unpublish (тот же DELETE-путь). Альтернативы: триггер с подсчётом активных строк (медленнее на каждой вставке), serializable-изоляция (дороже и капризнее в ретраях). Счётчик + CHECK — самый дешёвый и жёсткий инвариант.

**Example:**
```sql
CREATE TABLE user_listing_quota (
  user_id      bigint PRIMARY KEY REFERENCES users(id),
  active_count int NOT NULL CHECK (active_count >= 0 AND active_count <= 10)
);
-- публикация: одна транзакция
UPDATE user_listing_quota
   SET active_count = active_count + 1
 WHERE user_id = :uid AND active_count < 10;  -- 0 строк => квота исчерпана
-- row-level lock на строке квоты сериализует конкурентные публикации
UPDATE listings SET status = 'published', published_at = now()
 WHERE id = :listing_id AND seller_id = :uid AND status = 'draft';
-- unpublish: DELETE + декремент в той же транзакции
```

### Pattern 3: Adjacency list + recursive CTE (дерево категорий)

**What:** Рубрикатор хранится как `categories(id, parent_id, name, path)`: источник правды — `parent_id`; `path` (материализованный путь типа `/electronics/phones/`) — денормализация, пересчитываемая при редких admin-правках, для дешёвого фильтра «всё поддерево» в поиске (`path LIKE '/electronics/%'`).
**When to use:** Администрируемые деревья малой глубины (рубрикаторы обычно 2–4 уровня) с редкими правками и частыми чтениями.
**Trade-offs:** Nested sets дают subtree-чтение без CTE, но каждая вставка/перемещение переписывает половину таблицы — для admin-редактируемого дерева это потеря. Closure table избыточен для глубины 2–3. Adjacency + recursive CTE — стандартная прагматика (подтверждено несколькими comparison-обзорами моделей иерархий в SQL).

**Example:**
```sql
-- поддерево категории (навигация, фильтр поиска)
WITH RECURSIVE subtree AS (
  SELECT id, path FROM categories WHERE id = :root_id
  UNION ALL
  SELECT c.id, c.path FROM categories c
    JOIN subtree s ON c.parent_id = s.id
)
SELECT * FROM subtree;
-- быстрый вариант для поиска: WHERE l.category_path LIKE (SELECT path FROM categories WHERE id=:root) || '%'
```

## Data Flow

### Request Flow

```
[Пользователь публикует объявление]
    ↓
[Web UI] → [API layer] → [Listings module]
    ↓                         ↓
[Ответ 201/409-квота] ← [Транзакция БД: квота(+1) → status=published → индекс]
    ↓
(SSR-страница объявления; при внешнем поисковике — outbox → indexer)

[Пользователь ищет]
    ↓
[Web UI] → [Search module (read-side)] → [Postgres FTS + фильтры btree]
    ↓                                            ↓
[SSR-список объявлений] ← [ранжирование + пагинация ← ts_rank]
```

### State Management

```
[Listing state machine — единственный источник статуса в БД]
 draft ──publish(квота≤10)──▶ published ──unpublish──▶ (строка УДАЛЕНА из БД)
   │                            │
   └──delete──▶ (удалено)       └──delete──▶ (удалено)
[Client state]: web-first, SSR страниц объявлений и выдачи (SEO — основной
канал классифайдс); интерактив аккаунта — прогрессивное улучшение.
```

### Key Data Flows

1. **Публикация:** UI → Listings API → одна транзакция: `UPDATE quota` → `UPDATE listings SET status='published'` → (Phase 2) запись события в outbox. Неудача квоты откатывает всё; индекс не может «увидеть» объявление раньше БД.
2. **Снятие с публикации (PRD: удаление из БД):** UI → Listings API → транзакция: `DELETE FROM listings` + `UPDATE quota SET active_count = active_count - 1` + (Phase 2) событие удаления в outbox → indexer удаляет документ из индекса. Диалоги сообщений переживают удаление: `conversations.listing_id = ON DELETE SET NULL`, заголовок предмета денормализован в `conversations.listing_title_snapshot` при создании диалога.
3. **Поиск:** UI → Search API → `tsvector(title, description)` с GIN-индексом + btree по `(city_id, category_path prefix, price)` → сортировка по `ts_rank`/дате → пагинация keyset. Справочники (категории, города) читаются из кэша — они маленькие и почти неизменные.
4. **Администрирование справочников:** Admin UI → Catalog/Geo API → валидация использования (`RESTRICT`: нельзя удалить категорию/город, на которые ссылаются объявления; UI показывает счётчик использования и предлагает «скрыть» вместо удаления) → инвалидация кэша справочников.
5. **Сообщения:** UI автора → Messaging API → INSERT в `messages` (≤512, проверка схемы) → непрочитанные получателя; Phase 1 получатель видит входящие при загрузке/обновлении; Phase 2 — push через SSE/WebSocket за интерфейсом транспорта.

## Suggested Build Order

Порядок обусловлен зависимостями данных и инвариантов; каждый следующий компонент опирается на предыдущий:

1. **Identity & Profile + схема БД** — фундамент: `users` (обязательные имя/телеф/e-mail), миграции, конвенции. Ничего ниже не существует без пользователя.
2. **Catalog (дерево категорий) + Geo (города)** — справочники, на которые ссылаются объявления. Admin-CRUD обоих можно дать в одной фазе: технически идентичны (reference data + RESTRICT). `path`-денормализация категорий закладывается сразу — retrofit дорог.
3. **Listings: CRUD + квота + publish/unpublish (hard delete)** — ядро домена. Транзакция квоты и семантика `DELETE` (включая `SET NULL`-политику для будущих диалогов) должны появиться здесь, а не позже: `conversations.listing_id` создаётся в следующей фазе со ссылкой на уже жёсткую политику удаления.
4. **Search (read-side)** — требует наполненных listings: Postgres FTS + фильтры по поддереву/городу/цене. Приносит первую пользовательскую ценность «найти чужое объявление».
5. **Messaging** — требует users + listings (контекст диалога, снапшот заголовка при создании диалога, `ON DELETE SET NULL`).
6. **Admin Console (полировка) + кэш справочников + SSR/SEO страниц** — кросс-режимный слой поверх готовых модулей; кэширование справочников тривиально, потому что они читаются через контракты.
7. **Позже, по нагрузке (не фаза MVP):** внешний поисковый движок через шов `SearchIndex` + outbox; SSE/WebSocket-транспорт сообщений.

Ключевое правило порядка: **инварианты (квота, hard delete, ссылочная целостность) проектируются в той фазе, где появляется владеющая ими таблица** — retrofit квоты или политики удаления после появления messaging/search дороже в разы.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0–1k users | Монолит + один Postgres. Поиск = Postgres FTS. Никаких внешних движков, очередей и кэшей — ранняя оптимизация здесь вредит. |
| 1k–100k users | Тюнинг запросов и индексов; кэш справочников (категории/городы) в памяти процесса; read-replica БД для поисковых чтений; кэш SSR-страниц выдачи. Структура не меняется. |
| 100k+ users (PRD: до 1M) | Выделение поискового движка (Meilisearch/Typesense — typo-tolerance и фасеты из коробки, минимальный ops; Elasticsearch — только если потребуется log-scale) через уже существующий шов `SearchIndex` + outbox; Stateless-апп-тир за LB горизонтально; при необходимости — партиционирование `listings` по городу/датам; транспорт сообщений → SSE (однонаправленный пуш) или WebSocket + Redis pub/sub при полноценном чате. |

### Scaling Priorities

1. **First bottleneck — поиск (read-heavy).** Классифайдс читают в десятки раз чаще, чем пишут. Порядок: индексы GIN/btree → read-replica → выделенный движок. Консенсус источников: Postgres FTS уверенно тянет первые ~100K объявлений (часто до нескольких сотен тысяч строк) — этого хватит надолго.
2. **Second bottleneck — опрос входящих сообщений.** Наивный polling каждым пользователем генерирует постоянный фон запросов. Порядок: кэш счётчика непрочитанных → SSE-пуш → WebSocket только при полноценном realtime-чате.
3. **Записи мало, и PRD это фиксирует:** квота ≤10 активных на пользователя математически ограничивает таблицу `listings` (~≤10M строк на 1M пользователей, реально сильно меньше — не все публикуют). Это архитектурный подарок: write-путь и размер главной таблицы лимитированы требованиями. Кэш/шардинг записей не нужен вовсе.

## Anti-Patterns

### Anti-Pattern 1: Микросервисы с первого дня

**What people do:** Сразу строят «как Avito/eBay»: отдельные сервисы объявлений, поиска, чата, общение по сети.
**Why it's wrong:** Без нагрузочных данных границы угадываются неправильно; распределённые транзакции убивают главные инварианты этого домена (квота+публикация атомарны; удаление из БД+индекса согласованы). Fowler: почти все успешные microservice-истории начинались с монолита, который вырос и был разбит.
**Do this instead:** Модульный монолит с контрактами модулей; выделение Search позже — через заранее спроектированный интерфейс `SearchIndex`.

### Anti-Pattern 2: Soft delete (`deleted_at`) для объявлений

**What people do:** «На всякий случай» помечают снятые с публикации объявления флагом `deleted_at` вместо удаления.
**Why it's wrong:** Прямо нарушает PRD (снятие с публикации = удаление из БД, архива нет). Плюс классика (brandur.org, Stripe/Heroku-практика): предикат `deleted_at IS NULL` протекает в каждый запрос и его забывают; внешние ключи перестают что-либо гарантировать; undelete на практике почти никогда не работает, потому что у удаления есть побочные эффекты вне БД (индекс, кэши).
**Do this instead:** Честный `DELETE` в транзакции; вопросы поддержки/отладки решать отдельно (если когда-нибудь понадобится аудит — отдельная таблица-снимок, но это изменение PRD, а не молчаливое отступление).

### Anti-Pattern 3: Внешний поисковый движок и WebSocket-чат в MVP

**What people do:** Ставят Elasticsearch кластер и Socket.io-инфраструктуру до первого пользователя.
**Why it's wrong:** Двойная запись (БД + индекс) без outbox даёт рассинхрон; ops-стоимость движка и persistent-соединений высока; PRD не требует realtime — только «читает/пишет сообщения».
**Do this instead:** Postgres FTS сейчас; интерфейс `SearchIndex` и место под outbox — в схеме с первого дня, чтобы апгрейд был добавлением реализации, а не рефакторингом. Транспорт сообщений: HTTP → (при необходимости) SSE → WebSocket.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Поисковый движок (Meilisearch/Typesense, Phase 2+) | Indexer-воркер читает outbox, пишет/удаляет документы | Idempotent по listing_id; удаление документа обязано следовать за hard delete |
| Email/SMS-шлюз (верификация, уведомления — вне PRD MVP) | Прямой API-клиент за интерфейсом | Не блокирует пользовательские операции |
| Объектное хранилище изображений (вне PRD: обязательных полей изображений нет) | Приfuture-фазе: upload → S3-совместимое хранилище + CDN | Если появятся — hard delete обязан каскадировать и на блобы; заложить в lifecycle сейчас не нужно |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Listings ↔ Catalog/Geo | Прямой вызов контракта (in-process); FK в БД | FK `RESTRICT`: объявление ссылается только на существующие листовые категорию и город |
| Messaging ↔ Listings | Контракт `ListingService` (заголовок/владелец для снапшота) | Messaging не читает таблицу listings; переживает hard delete через `SET NULL` + снапшот |
| Search ↔ Listings | Через БД (Phase 1) / outbox-события (Phase 2) | Search — read-only модуль; никогда не пишет в доменные таблицы |
| Admin ↔ Catalog/Geo | Те же контракты + admin-политики | Удаление используемого справочника запрещено на уровне БД, а не только UI |

## Sources

- Kanopy Labs — How to Build a Classified Ads Marketplace (webfetch, полный текст): компонентный состав, read-heavy профиль, Postgres FTS до ~100K объявлений, lifecycle статусов, messaging-паттерны классифайдс — MEDIUM (практический гайд, сходится с остальными).
- Brandur Leach — Soft Deletion Probably Isn't Worth It (brandur.org, webfetch, полный текст, 2022): аргументация против soft delete, паттерн deleted_record, FK-целостность — MEDIUM (инженер Stripe, перекликается с GDPR-обзорами).
- PostgreSQL Official Docs — Transaction Isolation (postgresql.org/docs/current/transaction-iso.html): уровни изоляции, сериализуемость как основа для проверки инвариантов конкурентности — HIGH.
- Stack Overflow — «Limit rows with certain values in database», «only one active row per user with Doctrine and PostgreSQL»: паттерны `HAVING count(*)` + `FOR NO KEY UPDATE` для капов на группу строк — LOW→MEDIUM (практика сообщества, несколько независимых ответов).
- TarkovTracker migration (GitHub) — продакшн-пример триггера-капа активных токенов на пользователя — LOW (один пример, но реальный код в проде).
- Comparison-обзоры моделей иерархий в SQL (itfromzero.com, mironsoft.de, Stack Overflow «Managing hierarchies»): adjacency/materialized path/nested sets/closure table, trade-offs чтения/записи — MEDIUM (3+ независимых источника сходятся).
- Meilisearch docs — сравнения с PostgreSQL FTS и альтернативами (meilisearch.com/docs/resources/comparisons) + devtoolsguide.com, paradedb.com: тиринг поисковых решений — MEDIUM (вендор + независимые обзоры сходятся в консенсусе).
- Design Gurus / techscreen / back4app — WebSocket vs SSE vs polling: спектр транспортов realtime — MEDIUM (консенсус: не дефолтить WebSocket без двунаправленной нагрузки).
- Martin Fowler — Monolith First (martinfowler.com/bliki/MonolithFirst.html) + практические гайды 2025–2026 (milanjovanovic.tech и др.): модульный монолит как старт, скейлинг монолита тюнингом/кэшем/репликами — MEDIUM.

---
*Architecture research for: private classifieds web marketplace*
*Researched: 2026-11-18*
