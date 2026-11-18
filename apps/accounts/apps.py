from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Аккаунты и профиль пользователя (модели — Phase 2: custom User). Граница: чужие таблицы — только через сервис-функцию владельца (Pattern 3)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
