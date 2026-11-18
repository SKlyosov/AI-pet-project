# Phase 1 — API Coverage

**Detected signal:** `{"noun":"rest"}` — сработало на «Django **REST** Framework» в ADR/планах (выбор стека D-01/D-03).

No external API integration: Phase 1 — инфраструктурная фаза (Django-скелет, docker-compose, CI, миграции); Django REST Framework — локальный фреймворк для будущих СОБСТВЕННЫХ JSON-эндпоинтов (фазы 7–8), а не интеграция внешнего API; внешних сервисов (платежи, почта, S3, карты) в scope фазы нет — MinIO/S3 появляется в Phase 5, e-mail — в Phase 8 и будут покрыты их COVERAGE-матрицами.
