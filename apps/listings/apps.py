from django.apps import AppConfig


class ListingsConfig(AppConfig):
    """Объявления (модели — Phase 4). Граница: чужие таблицы — только через сервис-функцию владельца (Pattern 3)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.listings"
    label = "listings"
