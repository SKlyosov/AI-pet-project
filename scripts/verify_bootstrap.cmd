@echo off
rem Single-command bootstrap acceptance for phase 1 skeleton: SC-2, SC-4.
rem Run from the repository root; no arguments.
setlocal

echo [1/7] Reset pgdata volume: docker compose down -v
docker compose down -v
if errorlevel 1 exit /b 1

echo [2/7] Fresh start: docker compose up -d --build --wait
docker compose up -d --build --wait
if errorlevel 1 exit /b 1

echo [3/7] Health-check: curl /healthz
curl -fsS http://localhost:8000/healthz
if errorlevel 1 exit /b 1

echo [4/7] Root SSR page: curl / (hit-counter marker)
curl -fsS http://localhost:8000/ | findstr /C:hit-counter
if errorlevel 1 exit /b 1

echo [5/7] Unapplied migrations (exit 0 = none): migrate --check
docker compose run --rm web python manage.py migrate --check
if errorlevel 1 exit /b 1

echo [6/7] Applied migrations (all [X]): showmigrations
docker compose run --rm web python manage.py showmigrations
if errorlevel 1 exit /b 1

echo BOOTSTRAP_OK
exit /b 0
