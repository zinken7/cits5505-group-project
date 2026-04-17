# WatchList Hub

**CITS5505 — Agile Web (group project)**  
A full-stack web application for tracking anime, games, and movies, discovering trending titles, and browsing public watchlists.

---

## Project description

**WatchList Hub** is a social watchlist platform where signed-in users maintain personal lists with statuses such as **Watching**, **Planned**, and **Completed**. The app combines server-rendered pages (Flask + Jinja) with a lightweight client layer (Vite, Tailwind, jQuery “UI Lite” components) and a versioned **REST API** (`/api/v1`) documented with **OpenAPI**.

Typical use cases:

- Manage a personal watchlist and profile.
- Explore catalog-style content and (where implemented) trending or social features via the API.
- Integrate or test clients using Swagger UI, ReDoc, or the raw OpenAPI JSON.

---

## Tech stack


| Layer                | Technologies                                                                                 |
| -------------------- | -------------------------------------------------------------------------------------------- |
| **Backend**          | Python 3, **Flask 3**, **Flask-SQLAlchemy**, **Flask-Login**, **Flask-WTF**, python-dotenv   |
| **Database**         | **SQLite** by default (`DATABASE_URL` configurable)                                          |
| **Server templates** | **Jinja2**, shared **layout** (`layout.html`) with navbar, flash messages, footer            |
| **Frontend tooling** | **Vite 8**, **Tailwind CSS v4** (`@tailwindcss/vite`)                                        |
| **Client JS**        | **jQuery** (CDN), modular **UI Lite** bundle (`frontend/components` → `app/static/js/ui.js`) |
| **Theming**          | CSS variables + `data-theme` on `<html>` (light / dark), see `frontend/src/theme/theme.js`   |
| **API**              | REST under `**/api/v1`**, **OpenAPI 3** spec at `/openapi.json`                              |
| **API docs (human)** | **Swagger UI** (`/docs/apis`), **ReDoc** (`/docs/apis/redoc`)                                |


---

## Repository layout (short)

```
app/                    # Flask application package
  routes/               # Server-rendered page blueprints (e.g. main, auth, docs)
  api/v1/               # REST API blueprint (prefix /api/v1)
  templates/            # Jinja templates (layout.html, blank_page.html, …)
  static/               # Static assets (built Vite output, ui.js, …)
frontend/
  src/                  # Vite entry (main.js, style.css, theme/)
  components/           # UI Lite jQuery components (merged by buildUI.py)
buildUI.py              # Concatenates frontend/components → app/static/js/ui.js
run.py                  # App entry: create_app() + dev server on port 5000
config.py               # Config classes (development / production / testing)
requirements.txt        # Python dependencies
.env.example            # Environment template
```

---

## Prerequisites

- **Python** 3.10+ recommended  
- **Node.js** 20+ and **npm** (for Vite/Tailwind and production builds)

---

## Getting started

### 1. Clone and virtual environment

```bash
git clone <repository-url>
cd cits5505-group-project

python -m venv .venv
# Windows:
#   .venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
```

Edit `.env` as needed. Common variables:


| Variable       | Purpose                                                        |
| -------------- | -------------------------------------------------------------- |
| `FLASK_ENV`    | `development` (default in `.env.example`) or `production`      |
| `SECRET_KEY`   | Flask secret; **change** in any shared or deployed environment |
| `DATABASE_URL` | SQLAlchemy URI; default SQLite: `sqlite:///watchlist.db`       |


`config.py` maps `FLASK_ENV` to config classes (e.g. development enables debug and Vite dev mode).

### 3. Run the Flask app

From the project root (with venv activated):

```bash
python run.py
```

The development server listens on **port 5000** by default. Open:

- **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)** — home  
- **[http://127.0.0.1:5000/login](http://127.0.0.1:5000/login)** — sign in (if auth routes are enabled)

Alternative (if you prefer the Flask CLI):

```bash
export FLASK_APP=run:app          # Windows: set FLASK_APP=run:app
export FLASK_ENV=development
flask run --port 5000
```

### 4. Frontend in development (recommended)

In **development** config, `**VITE_DEV_MODE`** is **enabled**. Templates load CSS/JS from the **Vite dev server** (`http://localhost:5173` by default). Run it in a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

Keep **both** processes running: Flask (`python run.py`) and Vite (`npm run dev`). If you only start Flask without Vite, styles/scripts may fail to load until you build assets (next section).

### 5. Build frontend assets (production or offline dev)

When `VITE_DEV_MODE` is **false** (e.g. production), the app serves hashed files from `app/static/dist/` using Vite’s manifest.

```bash
cd frontend
npm install
npm run build
```

From the **repository root**, merge UI Lite components into a single file for `layout.html`:

```bash
python buildUI.py
```

After a successful build you should have:

- `app/static/dist/` — Vite output (JS/CSS + `manifest.json`)  
- `app/static/js/ui.js` — generated UI Lite bundle

You can run Flask with `FLASK_ENV=production` (or development after a build, if you temporarily disable Vite dev mode in config) to verify production-like behaviour.

---

## Documentation URLs

After starting the app (`python run.py`), use:


| What                                         | URL                | Notes                             |
| -------------------------------------------- | ------------------ | --------------------------------- |
| **Docs hub** (overview links)                | `/docs`            | Chooses UI vs API docs            |
| **UI Kit** (components, `data-ui`, previews) | `/docs/ui`         | Interactive UI Lite documentation |
| **Swagger UI** (try REST API)                | `/docs/apis`       | Uses `/openapi.json`              |
| **ReDoc** (readable API reference)           | `/docs/apis/redoc` | Same spec, alternate UI           |
| **OpenAPI JSON** (machine-readable)          | `/openapi.json`    | For Postman, codegen, etc.        |


Legacy redirect: `**/ui-docs`** → `/docs/ui`.

---

## REST API base URL

All versioned REST endpoints are under:

```text
/api/v1
```

Example health/root behaviour is defined on the API blueprint (see `app/api/v1/root.py`). Use Swagger or OpenAPI for the full path list.

---

## Adding a new server-rendered page

1. **Template**
  - Copy `app/templates/blank_page.html` to a new file, e.g. `app/templates/my_feature.html`.  
  - Set `{% block title %}`, and put markup in `{% block content %}`.
2. **Route**
  Register a view in the appropriate blueprint (often `app/routes/main.py`):
3. **Navigation** (optional)
  Add a link in `app/templates/components/navbar.html` using `url_for('main.my_feature')` (adjust endpoint name to match your blueprint + function).
4. **Page-specific JS** (optional)
  - Use `<main id="app">` and `initApp` patterns from `frontend/src/core/app.js` if you add client bootstrapping, **or**  
  - Extend `{% block scripts %}` in a template that extends `base.html` / `layout.html` if you need extra scripts.

---

## UI Lite components (`ui.js`)

- Source files live in `**frontend/components/`** (plus `core.js`).  
- `**python buildUI.py**` concatenates them into `**app/static/js/ui.js**` (do not edit the bundle by hand).  
- Components are initialized with `**window.UI.init()**` (already invoked from `frontend/src/main.js` on DOM ready for `[data-ui]` elements).  
- `**npm run build**` does not replace `buildUI.py`; run `**buildUI.py**` whenever you change files under `frontend/components/`.

---

## Security and deployment notes

- Change `**SECRET_KEY**` and use a proper `**DATABASE_URL**` for staging/production.  
- Review **CORS**, **HTTPS**, and **cookie** settings before exposing the app publicly.  
- The default SQLite file path is suitable for local development only; use a managed database for production if required.

---

## License / course

This repository is maintained for **CITS5505 Agile Web Development**. Adjust licensing and attribution per your unit and group agreement.