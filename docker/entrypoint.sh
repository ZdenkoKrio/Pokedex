#!/usr/bin/env sh
set -e

# Migrácie pred štartom (SQLite – žiadne čakanie na DB netreba)
echo "→ Running migrations"
python pokedex/manage.py migrate --noinput

# Static files – ak máš nastavený STATIC_ROOT, toto ich nahrá
echo "→ Collecting static files"
python pokedex/manage.py collectstatic --noinput --clear || true

echo "→ Collecting pokemon api data"
python pokedex/manage.py sync_everything || true


echo "→ Create admin_moderate group"
python pokedex/manage.py setup_comment_moderators || true

# Spusti zvyšok (CMD z Dockerfile)
echo "→ Starting server"
exec "$@"