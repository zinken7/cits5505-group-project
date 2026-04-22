#!/bin/bash

# Exit immediately if a command fails
set -e

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Seeding media..."
python scripts/seed_media.py

echo "Seeding items..."
python scripts/seed_items.py

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