"""Общие настройки проекта (12-factor): всё окружение-зависимое — из env.

Секреты (SECRET_KEY, DSN БД/кэша) читаются ТОЛЬКО через django-environ —
литеральных паролей/ключей в settings-файлах нет (ASVS V14, T-01-03/SC).
Окружения dev/test/prod наследуют этот модуль.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

SECRET_KEY = env("DJANGO_SECRET_KEY")

# Безопасный дефолт: dev-окружение переопределяет на True.
DEBUG = False

ALLOWED_HOSTS: list[str] = []

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://cache:6379/0"),
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.core",
    # Доменные модули (D-04): граница модуля = владение своими таблицами;
    # модели появляются в фазах-владельцах (Pattern 4 — без фейковой схемы).
    "apps.accounts",
    "apps.catalog",
    "apps.geo",
    "apps.listings",
    "apps.search",
    "apps.messaging",
    "apps.moderation",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise — сразу после SecurityMiddleware (Pitfall 6, доки WhiteNoise).
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

USE_TZ = True

LANGUAGE_CODE = "ru-ru"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
