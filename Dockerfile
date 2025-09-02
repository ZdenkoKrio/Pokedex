FROM python:3.13-slim

# Pracovný adresár
WORKDIR /app

# Systémové knižnice (Pillow, kompilácia závislostí). Postgres balíky netreba.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Env pre Python/Django
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=pokedex.settings

# Závislosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Aplikácia
COPY . .

# (Voliteľné) build-time collectstatic – nevadí, ak zlyhá (napr. bez nastavených env)
RUN python pokedex/manage.py collectstatic --noinput || true

# Entrypoint spustí migrácie a collectstatic tesne pred štartom servera
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 8000

# Výchozí príkaz – dev server s autoreloadom (pre prod môžeš nahradiť gunicornom)
CMD ["python", "pokedex/manage.py", "runserver", "0.0.0.0:8000"]