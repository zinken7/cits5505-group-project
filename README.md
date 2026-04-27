# WatchList Hub

**CITS5505 — Agile Web (group project)**  
A full-stack web application for tracking anime, games, and movies, discovering trending titles, social features (friends, messages), and browsing public watchlists.

---

## Project description

**WatchList Hub** is a social watchlist platform where signed-in users maintain personal lists with statuses such as **Watching**, **Planned**, and **Completed**. The app combines server-rendered pages (Flask + Jinja) with a **Vite + Tailwind v4** bundle (design tokens, per-page CSS/JS entries) and a versioned **REST API** (`/api/v1`) documented with **OpenAPI**. Real-time chat uses **Flask-SocketIO** (async mode **threading** for compatibility with SQLite).

Typical use cases:

- Manage a personal watchlist and profile.
- Explore catalog content, search, and social features via pages and the API.
- Integrate or test clients using Swagger UI, ReDoc, or the raw OpenAPI JSON.

---

## For the team: work only in `app/`

**Do not edit anything under `frontend/`.** That folder is for the **UI Lite / Vite maintainer** only (Tailwind entry, theme, Vite page entries, component sources that feed `ui.js`).


| Area                   | Where                                                                                                                                     |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Routes & templates** | `app/routes/`, `app/templates/` — most app pages extend `**app_layout.html`**; marketing/docs-style pages extend `**base.html**` directly |
| **Page CSS / JS**      | `app/static/css/`, `app/static/js/` for page-specific assets; global helpers in `app/static/js/main.js`                                   |
| **UI in HTML**         | Tailwind classes in Jinja + `data-ui="…"` — see the **UI Kit** at `/docs/ui` in the running app                                           |


You **do not** run `buildUI.py` or change files under `frontend/` for normal feature work.  
You may run `**npm run dev`** (or use a built `app/static/dist/`) so Tailwind and Vite assets load — that is to **run** the app, not to edit `frontend/` sources unless you own that area.

---

## Tech stack


| Layer                | Technologies                                                                                                                                   |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend**          | Python 3, **Flask 3**, **Flask-SQLAlchemy**, **Flask-Login**, **Flask-WTF**, **Flask-SocketIO**, **Flask-Limiter**, python-dotenv              |
| **Database**         | **SQLite** by default (`DATABASE_URL` in `.env`)                                                                                               |
| **Real-time**        | **Flask-SocketIO** with `async_mode="threading"` (avoids eventlet monkey-patching issues with SQLite in-process)                               |
| **Server templates** | **Jinja2** — `base.html` (global shell), `app_layout.html` (sidebar + topbar for signed-in app)                                                |
| **Frontend tooling** | **Vite 8**, **Tailwind CSS v4** — entry `frontend/src/style.css`, page entries under `frontend/src/pages/`                                     |
| **Client JS**        | jQuery (where used), `**window.apiFetch`** for API calls, modular **UI Lite** (`frontend/components` → `app/static/js/ui.js` via `buildUI.py`) |
| **Theming**          | CSS variables + `data-theme` on `<html>` (light / dark), `frontend/src/theme/theme.js`                                                         |
| **API**              | REST under `/api/v1`, **OpenAPI 3** at `/openapi.json`                                                                                         |
| **API docs**         | **Swagger UI** (`/docs/apis`), **ReDoc** (`/docs/apis/redoc`)                                                                                  |


---

## Repository layout

```
app/                          # Flask application package
  __init__.py                 # create_app(), extensions, blueprints, db bootstrap
  extensions.py               # db, login, csrf, migrate, limiter, socketio
  routes/                     # main, auth, docs blueprints
  api/v1/                     # REST API (watchlist, users, friends, messages, catalog, …)
  models/                     # user, media, watchlist, friendship, message
  services/                   # business logic (watchlist, friends, messages, …)
  sockets/                    # Socket.IO handlers (e.g. chat)
  templates/                  # Jinja (dashboard, explore, profile, chat, …)
  static/
    css/                      # Page / feature CSS (some imported via Vite page entries)
    js/                       # Page scripts, main.js, ui.js (generated), landing.js, …
    dist/                     # Vite production build output (+ manifest)
  data/                       # JSON seed data (movies, anime, tvshow, users.json)
  openapi/                    # OpenAPI spec builder
frontend/                     # Vite + Tailwind — UI Lite maintainer only
  src/
    style.css                 # Tailwind v4 + design tokens + shared @layer components
    theme/theme.js
    pages/*.js                # Per-page Vite entries (import page CSS)
  components/                 # UI Lite sources → buildUI.py → app/static/js/ui.js
  vite.config.js
scripts/
  seeds.py                    # Seed DB from app/data/*.json (media + users/social)
  enrich_genres.py            # Optional genre enrichment workflow
  imdb_top250.py, merge_movie_data.py, download_posters.py
tests/                        # pytest (e.g. watchlist service, API envelope)
buildUI.py                    # Concatenates frontend/components → app/static/js/ui.js
run.py                        # Local server: create_app + socketio.run (port 5002)
run.sh                        # venv, optional seeds, Flask + Vite dev (two processes)
run_pro.sh                    # Production-style: build frontend, FLASK_ENV=production, Flask only
run.bat                       # Windows: venv, optional seeds, Flask + Vite in separate windows
config.py                     # Development / production / testing config
requirements.txt
.env.example
.github/workflows/          # CI (e.g. ui.js regeneration when components change)
```

---

## Prerequisites

- **Python** 3.10+ recommended  
- **Node.js** 20+ and **npm** (Vite / Tailwind and production builds)

---

## Getting started (scripts)

### macOS / Linux — dev (Flask + Vite)

```bash
chmod u+x run.sh
./run.sh
```

### macOS / Linux — production-style (built assets, LAN-friendly)

```bash
chmod u+x run_pro.sh
./run_pro.sh
```

### Windows

```cmd
run.bat
```

`**run.sh` / `run.bat**` will:

- Activate `.venv` and, if the DB has no media yet, run `**python scripts/seeds.py**` (loads `**app/data/*.json**` into SQLite).
- Start **Flask-SocketIO** (see `run.py`, default **port 5002**).
- `**run.sh` / `run.bat` only:** install frontend deps and start `**npm run dev`** (Vite, port **5173**).

`**run_pro.sh`** sets `FLASK_ENV=production`, runs `npm run build`, then `**python run.py**` only (no Vite dev server).

Open the app at **[http://127.0.0.1:5002](http://127.0.0.1:5002)** (or your machine’s LAN IP on the same port when using `run_pro.sh`).

---

## Manual setup (if you skip the scripts)

### 1. Clone and virtual environment

```bash
git clone <repository-url>
cd <your-repo-folder>

python -m venv .venv
# Windows:   .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
```


| Variable       | Purpose                                                                                                                           |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `FLASK_ENV`    | `development` (default) or `production`                                                                                           |
| `SECRET_KEY`   | Flask secret — **change** for shared or deployed environments                                                                     |
| `DATABASE_URL` | SQLAlchemy URI; default SQLite: `sqlite:///watchlist.db` (path is relative to the process **cwd** unless you use an absolute URI) |


### 3. Seed the database (first time or after wiping the DB file)

From the project root:

```bash
python scripts/seeds.py
```

Options (see `python scripts/seeds.py --help`): `--clear`, `--media-only`, `--users-only`, `--type movie|anime|tvshow`.

### 4. Run the Flask app

```bash
python run.py
```

Default dev URL: **[http://127.0.0.1:5002/](http://127.0.0.1:5002/)**

Flask CLI alternative:

```bash
export FLASK_APP=run:app    # Windows: set FLASK_APP=run:app
export FLASK_ENV=development
flask run --port 5002
```

### 5. Frontend in development

When `VITE_DEV_MODE` is **true** (development config), templates load CSS/JS from the Vite dev server (`**http://localhost:5173`** by default). In a **second** terminal:

```bash
cd frontend
npm install
npm run dev
```

Keep **both** Flask and Vite running during local UI work, **or** run a production build (next section) so assets load from `app/static/dist/`.

### 6. Build frontend assets

```bash
cd frontend
npm install
npm run build
```

From the **repository root**, regenerate the UI Lite bundle if you changed `frontend/components/`:

```bash
python buildUI.py
```

Outputs include `**app/static/dist/**` (hashed JS/CSS + manifest) and `**app/static/js/ui.js**`.

---

## Documentation URLs


| What                             | URL                |
| -------------------------------- | ------------------ |
| **Docs hub**                     | `/docs`            |
| **UI Kit** (`data-ui`, previews) | `/docs/ui`         |
| **Swagger UI**                   | `/docs/apis`       |
| **ReDoc**                        | `/docs/apis/redoc` |
| **OpenAPI JSON**                 | `/openapi.json`    |


---

## REST API base URL

```text
/api/v1
```

See `app/api/v1/` and OpenAPI for the full path list.

---

## New pages (reminder)

Follow the **“work only in `app/`”** section. Typical checklist:

- Route in `app/routes/` + template under `app/templates/` (extend `**app_layout.html`** for in-app pages, or `**base.html**` for standalone pages such as docs).
- Tailwind + `data-ui` in markup; see `/docs/ui`.
- Optional page CSS/JS: Vite page entry in `frontend/src/pages/` + template `{% block vite_page %}` — coordinate with the Vite maintainer if unsure.

---

## Adding a server-rendered page (short)

1. Copy an existing template (e.g. `dashboard.html`) as a starting point; set `{% extends %}` (`app_layout.html` or `base.html`), `{% block title %}`, and `{% block content %}` / `{% block vite_page %}` as needed.
2. Register the view in the right blueprint (often `app/routes/main.py`).
3. Optional: add nav in `app/templates/components/navbar.html` with `url_for(...)`.
4. Optional: extend `{% block vite_page %}` / `{% block scripts %}` for page-specific assets.

---

## UI Lite maintainer (`frontend/` + `ui.js`)

**Everyone else can skip this section.**

- Component sources: `frontend/components/*.js` (plus `core.js` if present).  
- `**python buildUI.py`** writes `**app/static/js/ui.js**` — do not edit `ui.js` by hand.  
- After component changes: `buildUI.py`; for production also `cd frontend && npm run build`.  
- Document components at `/docs/ui`.

---

## CI / GitHub Actions

Workflows may regenerate `**app/static/js/ui.js**` when `frontend/components/**` or `buildUI.py` changes. See `.github/workflows/`.

---

## Security and deployment

- Change `**SECRET_KEY**` and use a proper `**DATABASE_URL**` for staging/production.  
- Review **CORS**, **HTTPS**, and **cookies** before a public deployment.  
- `**run.py`** uses Werkzeug with `allow_unsafe_werkzeug=True` for local convenience; use a production WSGI/ASGI server and process manager for real deployments.  
- SQLite is fine for local development; use a managed database for production if you need concurrency and durability at scale.

---

## License / course

This repository is maintained for **CITS5505 Agile Web Development**. Adjust licensing and attribution per your unit and group agreement.