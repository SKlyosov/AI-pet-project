from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """Сообщения между продавцами и покупателями (модели — Phase 8). Граница: чужие таблицы — только через сервис-функцию владельца (Pattern 3)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.messaging"
    label = "messaging"
