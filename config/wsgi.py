"""WSGI-точка входа: gunicorn config.wsgi:application.

Безопасный дефолт вне dev; в контейнере DJANGO_SETTINGS_MODULE всегда
приходит из env (.env), так что setdefault не срабатывает.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
