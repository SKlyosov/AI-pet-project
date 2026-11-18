# glibc-slim строго: psycopg[binary] ставится manylinux-колёсами,
# на musl (alpine) не ставится (Anti-Pattern/A8). *-alpine — только db/cache.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements/ requirements/

# Единый dev-образ фазы 1: pytest/ruff/mypy работают в контейнере
# (docker-first workflow, Pitfall 8). Прод-образ — вне scope фазы (A12).
RUN pip install --no-cache-dir -r requirements/dev.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
