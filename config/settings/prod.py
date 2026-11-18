"""Прод-настройки (security baseline, T-01-05/T-01-06).

Наследует 12-factor базу (config.settings.base); включается через
DJANGO_SETTINGS_MODULE=config.settings.prod.
"""
from .base import *  # noqa: F401,F403

# «You must never enable debug in production» (Django deployment checklist, T-01-05).
DEBUG = False

# Pitfall 4: при DEBUG=False без подходящего ALLOWED_HOSTS любой health-probe
# получает 400. Явный список из env, не звёздочка (T-01-06); дефолт ограничен
# loopback-хостами и именем сервиса web внутри compose-сети.
ALLOWED_HOSTS = env.list(  # noqa: F405
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "web"],
)

# Security-флаги deployment checklist (для скелета).
SECURE_CONTENT_TYPE_NOSNIFF = True

# Включаются при появлении реального TLS-терминала (осознанно не включены в скелете):
# SESSION_COOKIE_SECURE / CSRF_COOKIE_SECURE / SECURE_SSL_REDIRECT /
# SECURE_HSTS_SECONDS / SECURE_HSTS_INCLUDE_SUBDOMAINS / SECURE_HSTS_PRELOAD.
#
# Примечание: SECURE_BROWSER_XSS_FILTER не существует в Django 5.2 (удалена в
# Django 4.0 — проверено по django.conf.global_settings); XSS-защита шаблонов
# фаз 5–6 обеспечивается Content-Security-Policy, а не X-XSS-Protection.
