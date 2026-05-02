#!/bin/bash

set -e

echo "Activating virtual environment..."
source .venv/bin/activate

# Force production mode — assets load from app/static/dist/ (built files)
# This is required so LAN devices can access CSS/JS (they can't reach localhost:5173)
export FLASK_ENV=production

if [ ! -d "migrations" ]; then
    echo "ERROR: migrations/ folder not found."
    echo "  This folder must be committed to git."
    echo "  Run: git add migrations/ && git commit -m 'add migrations'"
    exit 1
fi

echo "Applying database migrations..."
flask db upgrade

# Seed only when the media table is empty (fresh DB or wiped DB)
if ! python - <<'EOF'
import sys
sys.path.insert(0, ".")
from app import create_app
from app.models.media import Media
app = create_app()
with app.app_context():
    sys.exit(0 if Media.query.count() > 0 else 1)
EOF
then
    echo "Database empty — seeding initial data..."
    python scripts/seeds.py
else
    echo "Database already seeded — skipping."
fi

echo "Building frontend..."
cd frontend
npm install --silent
npm run build
cd ..

echo "VITE_DEV_MODE check:"
python - <<'PYEOF'
from app import create_app
app = create_app()
mode = app.config['VITE_DEV_MODE']
print(f"  VITE_DEV_MODE = {mode}")
if mode:
    print("  ERROR: still in dev mode, CSS will not load on LAN!")
    raise SystemExit(1)
else:
    print("  OK — serving built assets from /static/dist/")
PYEOF

echo "Starting server (accessible on LAN)..."
python run.py
