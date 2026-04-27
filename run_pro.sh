#!/bin/bash

set -e

echo "Activating virtual environment..."
source .venv/bin/activate

# Force production mode — assets load from app/static/dist/ (built files)
# This is required so LAN devices can access CSS/JS (they can't reach localhost:5173)
export FLASK_ENV=production

# Only seed on a fresh database
DB_FILE="instance/watchlist.db"
if [ ! -f "$DB_FILE" ] || ! python - <<'EOF'
import sys, os
sys.path.insert(0, ".")
from app import create_app
from app.models.media import Media
app = create_app()
with app.app_context():
    sys.exit(0 if Media.query.count() > 0 else 1)
EOF
then
    echo "Fresh database — running scripts/seeds.py (app/data -> DB)..."
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
