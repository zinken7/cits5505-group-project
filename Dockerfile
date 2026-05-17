# ── Stage 1: Build frontend assets ───────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /workspace
COPY . .

RUN cd frontend && npm ci && npm run build
# Output: /workspace/app/static/dist/


# ── Stage 2: Python application ───────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# System deps for Werkzeug/SQLAlchemy C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Overwrite with freshly built assets from stage 1
COPY --from=frontend-builder /workspace/app/static/dist/ ./app/static/dist/

RUN mkdir -p instance app/static/posters

EXPOSE 5002

CMD flask db upgrade \
 && (python -c 'from app import create_app; from app.models.media import Media; a=create_app(); a.app_context().push(); exit(0 if Media.query.count()>0 else 1)' \
     || python scripts/seeds.py) \
 && exec gunicorn -k gthread -w 1 --threads 100 -b 0.0.0.0:5002 wsgi:app
