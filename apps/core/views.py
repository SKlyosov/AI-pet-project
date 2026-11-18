from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

HOME_HITS_KEY = "core:home:hits"


@require_GET
def healthz(request):
    """Живость зависимостей: SELECT 1 в PostgreSQL + ping Redis.

    Ответ не раскрывает внутренностей (никаких версий/хостов/DSN —
    T-01-03): только {"status": "ok"/"fail"} и статус 200/503.
    """
    checks = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["db"] = "ok"
        cache.set("healthz:ping", "1", timeout=5)
        checks["cache"] = "ok"
    except Exception:
        return JsonResponse({"status": "fail", "checks": checks}, status=503)
    return JsonResponse({"status": "ok", "checks": checks})


def home(request):
    """Корневая SSR-страница со счётчиком просмотров (write+read в Redis)."""
    try:
        hits = cache.incr(HOME_HITS_KEY)
    except ValueError:
        # Ключа ещё нет — первый просмотр.
        cache.set(HOME_HITS_KEY, 1, timeout=None)
        hits = 1
    return render(request, "home.html", {"hits": hits})
