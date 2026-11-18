from django.apps import AppConfig


class ModerationConfig(AppConfig):
    """Модерация объявлений (модели — Phase 9). Граница: чужие таблицы — только через сервис-функцию владельца (Pattern 3)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.moderation"
    label = "moderation"
