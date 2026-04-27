#!/bin/bash

# Exit immediately if a command fails
set -e

echo "Activating virtual environment..."
source .venv/bin/activate

# Only seed on a fresh database — skip if Media rows already exist.
# To force a full reseed (e.g. after JSON edits): delete instance/watchlist.db first,
# or run:  python scripts/seeds.py --clear
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
    echo "Database already seeded — skipping seed scripts."
fi

echo "Starting backend..."
python run.py &
BACKEND_PID=$!

echo "Setting up frontend..."
cd frontend

npm install

echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

# Wait for both processes
wait