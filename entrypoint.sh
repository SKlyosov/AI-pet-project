#!/bin/sh
# Идемпотентный старт web-контейнера: миграции -> статика -> сервер.
# С аргументами (docker compose run --rm web <cmd>) выполняет команду
# вместо запуска gunicorn (миграции и collectstatic проходят как обычно).
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2
