"""Маршруты проекта: health-check, корневая SSR-страница, Django Admin (D-02)."""
from django.contrib import admin
from django.urls import path

from apps.core.views import healthz, home

urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    # Псевдоним без слэша: цели зондов (curl /healthz, compose healthcheck)
    # получают 200 с телом сразу, а не 301-редирект от APPEND_SLASH.
    path("healthz", healthz),
    path("", home, name="home"),
    path("admin/", admin.site.urls),
]
