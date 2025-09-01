#!/usr/bin/env bash
set -euo pipefail

if [ -n "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL je nastavené, preskakujem wait-for-db (predpokladá sa cloud DB)."
else
  echo "Čakám na Postgres na db:5432…"
  until nc -z db 5432; do
    sleep 0.5
  done
fi

echo "→ python manage.py migrate"
python manage.py migrate --noinput

echo "→ python manage.py collectstatic"
python manage.py collectstatic --noinput --clear

echo "→ gunicorn pokedex.wsgi:application"
exec gunicorn pokedex.wsgi:application \
  --config /app/docker/gunicorn.conf.py