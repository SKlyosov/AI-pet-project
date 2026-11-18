# AI-pet-project — сервис частных объявлений

Веб-сервис объявлений о продаже товаров и услуг **только для частных лиц**:
объявления частных продавцов не тонут среди коммерческих предложений и
находят покупателя. Требования проекта — `docs/PRD.md`, контекст и план
разработки — `.planning/`.

## Стек

- Python 3.13 / Django 5.2 LTS + Django REST Framework
- PostgreSQL 18 — единственная RDBMS; Redis 8 — кэш
- docker compose: gunicorn + WhiteNoise; статика без внешнего nginx

Обоснование выбора стека — [docs/adr/0001-choice-of-stack.md](docs/adr/0001-choice-of-stack.md).

## Быстрый старт

Нужны Docker и curl; Python на хосте не требуется — весь workflow идёт
через docker compose.

1. Скопируйте `.env.example` в `.env` (значения по умолчанию пригодны для
   локальной разработки):

    ```
    copy .env.example .env
    ```

    (Unix: `cp .env.example .env`)

2. Поднимите стек одной командой:

    ```
    docker compose up -d --build --wait
    ```

3. Проверьте живость приложения:

    ```
    curl http://localhost:8000/healthz
    ```

   Ожидается `{"status": "ok", "checks": {"db": "ok", "cache": "ok"}}`.

Приёмка скелета одной командой (перезапускает стек с чистой БД):
Windows — `scripts\verify_bootstrap.cmd`, Unix — `scripts/verify_bootstrap.sh`.

## Тесты и линтинг

Команды выполняются в контейнере `web`. Контейнер исполняет код, запечённый
в образ, — после изменения кода пересоберите его
(`docker compose build web` или повторный `docker compose up -d --build --wait`):

- тесты: `docker compose run --rm web pytest -x -q`
- линтер: `docker compose run --rm web ruff check .`
- типы: `docker compose run --rm web mypy .`
