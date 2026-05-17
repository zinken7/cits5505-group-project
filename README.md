<div align="center">

# WatchList Hub

**Track. Discover. Share.**

[![CI](https://img.shields.io/github/actions/workflow/status/zinken7/cits5505-group-project/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white)](https://github.com/zinken7/cits5505-group-project/actions/workflows/ci.yml) [![Python](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/) [![Flask](https://img.shields.io/badge/flask-3.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tailwind CSS](https://img.shields.io/badge/tailwindcss-v4-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/) [![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

A full-stack social platform for tracking **movies**, **anime**, and **TV shows** — with watchlists, real-time chat, friend system, and a versioned REST API.

[Features](#features) · [Quick Start](#quick-start) · [API Docs](#api--docs) · [Testing](#testing)

</div>

---

## Group Members

| UWA ID   | Name             | GitHub Username                                   |
|----------|------------------|---------------------------------------------------|
| 24814799 | Tyrone Tran      | [zinken7](https://github.com/zinken7)             |
| 24702635 | Aashritha Jangam | [aashritha463](https://github.com/aashritha463)   |
| 24643978 | Han Nguyen Thi   | [hnguyen-debug](https://github.com/hnguyen-debug) |
| 24769645 | Sarwesh Kattel   | [Sarwesh13](https://github.com/Sarwesh13)         |

---

## Features

- **Watchlist management** — six statuses per item: Watching, Planned, Completed, Dropped, On Hold, Rewatching
- **Social** — send friend requests, browse friends' public watchlists, share a watchlist via link
- **Real-time chat** — Socket.IO powered direct messaging between friends
- **Discover** — explore catalog by type and genre, trending rail based on community activity
- **Search** — full-text search across media titles and user profiles
- **Dark / Light theme** — system-aware with manual toggle
- **Admin panel** — manage media catalog and users, role hierarchy (user → admin → root)
- **REST API** — versioned `/api/v1` with OpenAPI 3 spec, Swagger UI, and ReDoc
- **Responsive** — works on mobile, tablet, and desktop

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.12, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate, Flask-Limiter |
| **Real-time** | Flask-SocketIO (`async_mode="threading"`) |
| **Database** | SQLite (default) — swappable via `DATABASE_URL` |
| **Frontend** | Vite 6, Tailwind CSS v4, CSS design tokens, per-page JS entries |
| **API** | REST `/api/v1`, OpenAPI 3, Swagger UI, ReDoc |
| **Auth** | Flask-Login, Flask-WTF CSRF, Werkzeug password hashing (scrypt) |
| **CI** | GitHub Actions — unit tests, Selenium tests, frontend build |
| **Deployment** | Docker + Docker Compose |

---

## Quick Start

### Docker (recommended)

```bash
# 1. Copy and configure secrets
cp .env.example .env
# Edit .env: set SECRET_KEY and ROOT_PASSWORD

# 2. Build and run (migrations + seeding run automatically)
docker compose up --build

# 3. Open http://localhost:5002
```

Subsequent starts (no code changes):
```bash
docker compose up -d      # start in background
docker compose down       # stop (data is preserved)
```

### Local development

**Prerequisites:** Python 3.12+, Node.js 20+

```bash
# Clone and set up environment
git clone https://github.com/zinken7/cits5505-group-project.git
cd cits5505-group-project
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Apply migrations and seed data
flask db upgrade
python scripts/seeds.py

# Terminal 1 — Flask
python run.py

# Terminal 2 — Vite dev server (for hot-reload CSS/JS)
cd frontend && npm install && npm run dev
```

Open **http://127.0.0.1:5002**

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-me` | Flask secret — **always change in production** |
| `FLASK_ENV` | `development` | `development` or `production` |
| `DATABASE_URL` | `sqlite:///watchlist.db` | SQLAlchemy database URI |
| `ROOT_USERNAME` | `root` | Bootstrap root account username |
| `ROOT_EMAIL` | `root@localhost` | Bootstrap root account email |
| `ROOT_PASSWORD` | `root-root-change-me` | Bootstrap root account password — **always change** |

---

## Project Structure

```
app/
├── api/v1/             # REST API — watchlist, users, friends, messages, catalog …
├── models/             # user, media, watchlist, friendship, message
├── routes/             # main, auth, admin blueprints
├── services/           # business logic layer
├── sockets/            # Socket.IO event handlers
├── templates/          # Jinja2 pages (dashboard, explore, profile, items …)
├── static/
│   ├── css/            # Page-specific CSS
│   ├── js/             # Page scripts + ui.js (auto-generated)
│   └── dist/           # Vite production build output
└── openapi/            # OpenAPI 3 spec builder

frontend/               # Vite + Tailwind — build tooling only
├── src/
│   ├── style.css       # Tailwind v4 + design tokens + shared components
│   └── pages/          # Per-page Vite entries
└── components/         # UI Lite sources → app/static/js/ui.js

migrations/             # Alembic migration files
scripts/                # seeds.py, download_posters.py, enrich_media.py …
tests/                  # pytest unit tests + Selenium integration tests
```

---

## API & Docs

All endpoints are under `/api/v1`. The full spec is generated at runtime.

| Interface | URL |
|---|---|
| Swagger UI | `/docs/apis` |
| ReDoc | `/docs/apis/redoc` |
| OpenAPI JSON | `/openapi.json` |
| UI component docs | `/docs/ui` |

---

## Testing

```bash
source .venv/bin/activate

# Unit + integration tests
pytest --ignore=tests/test_selenium.py -v

# Selenium end-to-end tests (requires built frontend)
cd frontend && npm run build && cd ..
pytest tests/test_selenium.py -v
```

The CI pipeline runs all three jobs automatically on every PR and push to `main`:
- **Frontend Build** — `npm ci && npm run build`
- **Unit Tests** — 75 pytest tests
- **Selenium Tests** — 19 end-to-end browser tests

---

## License

This project was developed for **CITS5505 Agile Web Development** at the University of Western Australia.
