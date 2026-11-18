"""Настройки для pytest/CI: быстрые хэшеры и автоперезагрузка статики.

env-дефолты указывают на localhost (GitHub Actions services слушают
localhost); при запуске через docker compose run значения приходят из
.env и переопределяют дефолты.
"""
import environ

from .base import *  # noqa: F401,F403

env = environ.Env()

# Pitfall 7: без этого WhiteNoise замедляет каждый прогон pytest.
WHITENOISE_AUTOREFRESH = True

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://classifieds:classifieds-dev-only@localhost:5432/classifieds",
    ),
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://localhost:6379/0"),
    }
}
