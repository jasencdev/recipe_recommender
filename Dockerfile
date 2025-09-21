# Multi-stage build: build frontend, then package Flask app

FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY food-recipe-recommender/app/frontend/package*.json ./
RUN npm ci
COPY food-recipe-recommender/app/frontend/ ./
RUN npm run build

FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENV=production \
    UV_LINK_MODE=copy \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# System deps (git optional), and clean up apt lists afterward
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml uv.lock ./
COPY food-recipe-recommender ./food-recipe-recommender

# Install uv and Python deps into system site-packages
RUN pip install --no-cache-dir uv \
    && uv sync

# Copy built frontend into Flask templates/static
COPY --from=frontend-build /app/frontend/dist/index.html /app/food-recipe-recommender/app/templates/index.html
COPY --from=frontend-build /app/frontend/dist/assets /app/food-recipe-recommender/app/static/assets

# Port for Railway (uses $PORT). Default to 8080 for local
ENV PORT=8080
EXPOSE 8080

WORKDIR /app/food-recipe-recommender/app

# Start with Gunicorn; use shell form for env var expansion
CMD ["sh","-c","uv run waitress-serve --listen=0.0.0.0:${PORT:-8080} app:app"]
