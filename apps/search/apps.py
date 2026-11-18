from django.apps import AppConfig


class SearchConfig(AppConfig):
    """Поиск объявлений (модели — Phase 7). Граница: чужие таблицы — только через сервис-функцию владельца (Pattern 3)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.search"
    label = "search"
