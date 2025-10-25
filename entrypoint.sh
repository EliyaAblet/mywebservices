#!/usr/bin/env bash
set -e

host="${DB_HOST:-db}"
port="${DB_PORT:-5432}"

echo "Waiting for Postgres at $host:$port ..."
until nc -z "$host" "$port"; do
  sleep 0.5
done
echo "Postgres is up."

echo "Applying migrations..."
python manage.py migrate --noinput

if [ "${DJANGO_SUPERUSER_CREATE:-false}" = "true" ]; then
  python manage.py createsuperuser --noinput || true
fi

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000

