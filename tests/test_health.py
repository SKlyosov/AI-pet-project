"""Wave 0: интеграционные тесты скелета — /healthz и корневая страница.

Оба теста исполняются против реальных db/cache из compose-сети
(env из .env): SELECT 1 в PostgreSQL и write/read в Redis.
"""
import pytest


@pytest.mark.django_db
def test_healthz_ok(client):
    response = client.get("/healthz/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["checks"]["db"] == "ok"
    assert payload["checks"]["cache"] == "ok"


def test_home_counter_increments(client):
    first = client.get("/")
    second = client.get("/")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.context["hits"] == first.context["hits"] + 1
