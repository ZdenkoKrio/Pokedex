# Pokédex Project

## 📖 About the Project
This is a custom-built **Pokédex web application** built with **Django**.  
The project integrates with [PokeAPI](https://pokeapi.co/) and provides a rich, user-friendly interface to explore Pokémon.  

Key features:
- Full **Pokédex detail pages** with:
  - Sprites (classic, shiny, animated, official artwork)
  - Base stats, abilities, and types
  - Evolution chains with clickable sprites
  - Forms & varieties (Alolan, Galarian, etc.) with mini previews
  - Moves (grouped by learn method, with annotated details such as type/power/accuracy)
  - Encounter locations per game version
  - Pokédex flavor texts of game descriptions
- **User system**:
  - Registered users can **build their Pokémon teams**
  - Teams can be **liked** and **commented** by other users
  - Favorite Pokémon functionality
- **Smart caching** of API responses to reduce redundant PokeAPI calls
- Clear separation of concerns in project structure:
  - `services/detail` → helpers for preparing API data for views
  - `services/cache` → DB upserts and syncing logic
  - `services/api` → cached PokeAPI client

---



## ⚙️ Running the Project (without Docker)

### 1. Clone and install dependencies
```bash
git clone <your-repo-url>
cd pokedex
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py sync_everything
python manage.py setup_comments_moderators (optional)
python manage.py runserver
```

### 2. Run migrations and setup project
```bash
python manage.py migrate
python manage.py sync_everything
python manage.py setup_comments_moderators (optional)
python manage.py runserver
```

### 3. Run project
```bash
python manage.py runserver
```


## ⚙️ Running the Project (with Docker)

### 1. Build container and start the app
```bash
docker-compose build
docker-compose up
```


## Notes & Design Choices

### Project structure
We carefully separated responsibilities into:
- `services/detail` – view helpers (data shaping for templates, no DB writes)
- `services/cache` – DB sync layer (upserts Pokémon into local cache)
- `services/api` – thin HTTP client

This makes the project maintainable, testable, and easy to extend.

### Caching layer
To avoid hitting the PokeAPI too often, we use a thin caching layer that keeps API responses locally and normalizes them for rendering.

### Interactive Pokémon features
Registered users can:
- Build and save their own Pokémon teams
- Like and comment on others’ teams
- Favorite Pokémon for quick access

### UI touches we’re proud of
- Evolution chain previews with clickable sprites
- Forms/varieties mini-thumbnails (similar to Alolan/Galarian views)
- Pokédex flavor


## What I’m Proud Of

- **Clean separation** of API detail helpers vs. DB sync logic  
- **Caching strategy** that makes browsing smooth and efficient  
- **Interactive community features** (teams, likes, comments) that go beyond a static Pokédex  
- **Modular design** that makes it easy to add future features (like battle simulations or leaderboard mechanics)  


