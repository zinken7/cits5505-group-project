#!/bin/bash

# Exit immediately if a command fails
set -e

echo "Activating virtual environment..."
source .venv/bin/activate

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
