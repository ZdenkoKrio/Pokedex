# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# systémové knižnice
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev libjpeg-dev zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# python závislosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Django env (uprav ak máš iný modul so settings)
ENV DJANGO_SETTINGS_MODULE=pokedex.settings \
    PYTHONUNBUFFERED=1


RUN python pokedex/manage.py collectstatic --noinput || true

EXPOSE 8000

CMD ["python", "pokedex/manage.py", "runserver", "0.0.0.0:8000"]