# Pokédex (Django)

Malá Django aplikácia, ktorá zobrazuje detail Pokémonov z PokeAPI a ukladá “thin cache”
do lokálnej DB. Má prehľadné detail stránky (štatistiky, moves, encounters, evolúcie,
formy/variety, flavor text carousel).

## Požiadavky

- Python 3.12+ (projekt beží aj na 3.13)
- Django 5.x
- (voliteľné) Docker / Docker Compose

> DB: projekt funguje **out-of-the-box na SQLite**. Ak chceš Postgres, pozri sekciu
> `docker-compose` nižšie.

---

## Rýchly štart (lokálne, bez Dockeru)

```bash
# 1) vytvor a aktivuj virtuálne prostredie
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) nainštaluj závislosti
pip install -U pip
pip install -r requirements.txt  # ak súbor máš
# (ak requirements.txt nemáš, aspoň:)
# pip install "Django>=5.0,<6.0" requests

# 3) migrácie
python manage.py migrate

# 3) cache dat + vytvorenie group
python manage.py sync_everything
python manage.py setup_comment_moderators

# 5) štart
python manage.py runserver 
