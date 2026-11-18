from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Рубрикатор товаров и услуг (модели — Phase 3). Граница: чужие таблицы — только через сервис-функцию владельца (Pattern 3)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog"
    label = "catalog"
