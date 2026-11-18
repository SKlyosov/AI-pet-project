"""Настройки локальной разработки."""
from .base import *

DEBUG = True

# Pitfall 4: хосты пробы явно перечислены — иначе запрос healthz даст 400.
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "web"]

# WhiteNoise: отключает runserver-обработчик статики в dev (доки WhiteNoise).
INSTALLED_APPS = ["whitenoise.runserver_nostatic", *INSTALLED_APPS]
