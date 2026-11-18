#!/bin/sh
# Однокомандная приёмка скелета фазы 1: SC-2 (одна команда + health-check)
# и SC-4 (воспроизводимая первая миграция на чистой базе).
# Запускать из корня репозитория; аргументов нет.
set -e

echo "[1/7] Сброс тома pgdata: docker compose down -v"
docker compose down -v

echo "[2/7] Подъём с нуля: docker compose up -d --build --wait"
docker compose up -d --build --wait

echo "[3/7] Health-check: curl /healthz"
curl -fsS http://localhost:8000/healthz
echo ""

echo "[4/7] Корневая SSR-страница: curl / (маркер hit-counter)"
curl -fsS http://localhost:8000/ | grep hit-counter

echo "[5/7] Неприменённые миграции (exit 0 = нет): migrate --check"
docker compose run --rm web python manage.py migrate --check

echo "[6/7] Применённые миграции (все [X]): showmigrations"
docker compose run --rm web python manage.py showmigrations

echo "BOOTSTRAP_OK"
