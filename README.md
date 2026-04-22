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

## ⛔ For the team: work only in `app/`

**Do not edit anything under `frontend/`.** That folder is for the **UI Lite / Vite maintainer** only (component sources, theme pipeline, production bundle).


| You should use           |                                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------------- |
| **Routes & templates**   | `app/routes/`, `app/templates/` (e.g. extend `layout.html`, copy `blank_page.html`)                     |
| **Optional page CSS/JS** | `app/static/css/main.css`, `app/static/js/main.js` (loaded on layout pages)                             |
| **UI in HTML**           | Tailwind classes in Jinja + `**data-ui="…"`** — see the **UI Kit** at `**/docs/ui`** in the running app |


You **do not** run `buildUI.py` or change files under `frontend/` for normal feature work.  
You may still run `**npm run dev`** (or rely on a built `app/static/dist/`) so Tailwind and the Vite bundle load — that is only to **run** the app, not to edit the `frontend/` sources.

---

## Tech stack


| Layer                          | Technologies                                                                                 |
| ------------------------------ | -------------------------------------------------------------------------------------------- |
| **Backend**                    | Python 3, **Flask 3**, **Flask-SQLAlchemy**, **Flask-Login**, **Flask-WTF**, python-dotenv   |
| **Database**                   | **SQLite** by default (`DATABASE_URL` configurable)                                          |
| **Server templates**           | **Jinja2**, shared **layout** (`layout.html`) with navbar, flash messages, footer            |
| **Frontend tooling**           | **Vite 8**, **Tailwind CSS v4** (`@tailwindcss/vite`)                                        |
| **Client JS**                  | **jQuery** (CDN), modular **UI Lite** bundle (`frontend/components` → `app/static/js/ui.js`) |
| **Page-level static (layout)** | `app/static/css/main.css`, `app/static/js/main.js` — optional; see callout above             |
| **Theming**                    | CSS variables + `data-theme` on `<html>` (light / dark), see `frontend/src/theme/theme.js`   |
| **API**                        | REST under `**/api/v1`**, **OpenAPI 3** spec at `/openapi.json`                              |
| **API docs (human)**           | **Swagger UI** (`/docs/apis`), **ReDoc** (`/docs/apis/redoc`)                                |


---

## Repository layout (short)

```
app/                    # Flask application package
  routes/               # Server-rendered page blueprints (e.g. main, auth, docs)
  api/v1/               # REST API blueprint (prefix /api/v1)
  templates/            # Jinja templates (layout.html, blank_page.html, …)
  static/
    css/main.css        # Team overrides (loaded after Vite/Tailwind on layout pages)
    js/main.js          # Team scripts (after ui.js; jQuery + window.UI available)
    js/ui.js            # UI Lite bundle (generated — do not edit by hand)
frontend/               # UI Lite maintainer + Vite only — do not edit for normal page work
  src/                  # Vite entry (theme, UI.init, dashboard hooks)
  components/           # UI Lite sources → buildUI.py → app/static/js/ui.js
buildUI.py              # Concatenates frontend/components → app/static/js/ui.js
run.py                  # App entry: create_app() + dev server on port 5000
config.py               # Config classes (development / production / testing)
requirements.txt        # Python dependencies
.env.example            # Environment template
.github/workflows/      # e.g. regenerate ui.js on push when components change
```

---

## Prerequisites

- **Python** 3.10+ recommended  
- **Node.js** 20+ and **npm** (for Vite/Tailwind and production builds)

---

## Getting started

For **faster setup**, use one of the provided startup scripts instead of manual steps:

#### macOS / Linux:
```
chmod u+x run.sh
./run.sh
```

#### Windows:
```
run.bat
```

Both scripts will:
- Seed the database with media and items data
- Start the **Flask backend** on port 5000
- Start the **Vite dev server** on port 5173
- Keep both processes running

**The demo will show in address: [http://127.0.0.1:5000](http://127.0.0.1:5000)**

If scripts don't work or you prefer manual control, follow steps below.

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

## New pages (reminder)

Follow the **“For the team: work only in `app/`”** section above. Typical checklist:

- **Route** + **template** (`layout.html` / `blank_page.html`).
- **Tailwind** + `**data-ui`** in markup; see `/docs/ui`.
- Optional `**app/static/js/main.js**` / `**app/static/css/main.css**`.

Templates that **extend `base.html` only** (e.g. some docs views) do not automatically load `main.css` / `main.js` — add the same `<link>` / `<script>` as in `layout.html` if you need them.

---

## Adding a new server-rendered page

1. **Template**
  - Copy `app/templates/blank_page.html` to a new file, e.g. `app/templates/my_feature.html`.  
  - Set `{% block title %}`, and put markup in `{% block content %}`.
2. **Route**
  Register a view in the appropriate blueprint (often `app/routes/main.py`):
3. **Navigation** (optional)
  Add a link in `app/templates/components/navbar.html` using `url_for('main.my_feature')` (adjust endpoint name to match your blueprint + function).
4. **Scripts and styles** (optional)
  - Edit `**app/static/js/main.js`** and `**app/static/css/main.css**` only.  
  - Extend `{% block scripts %}` in a template if you must load an extra third-party script from a URL.

---

## UI Lite maintainer (`frontend/` + `ui.js`)

**Everyone else can skip this section.** Only the person maintaining UI Lite touches `frontend/`.

- Component sources: `**frontend/components/*.js`** (plus `core.js`).  
- `**python buildUI.py**` writes `**app/static/js/ui.js**` — never edit that file by hand.  
- `**window.UI.init()**` runs from the Vite bundle on `[data-ui]` elements.  
- After changing components, run `**buildUI.py**`; for production CSS/JS also `**cd frontend && npm run build**`.  
- Document new or updated components at `**/docs/ui**`.

---

## CI / GitHub Actions

Workflows may regenerate `**app/static/js/ui.js**` when `frontend/components/**` or `buildUI.py` changes — relevant for the **UI Lite maintainer** only. See `.github/workflows/`.

---

## Security and deployment notes

- Change `**SECRET_KEY`** and use a proper `**DATABASE_URL**` for staging/production.  
- Review **CORS**, **HTTPS**, and **cookie** settings before exposing the app publicly.  
- The default SQLite file path is suitable for local development only; use a managed database for production if required.

---

## License / course

This repository is maintained for **CITS5505 Agile Web Development**. Adjust licensing and attribution per your unit and group agreement.