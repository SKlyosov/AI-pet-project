from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Ядро проекта: health-check и общая инфраструктура (без доменных таблиц)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
