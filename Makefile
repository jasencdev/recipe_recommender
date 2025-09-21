SHELL := /bin/bash

# Backend
test:
	uv run pytest -q -p no:cacheprovider

test-cov:
	uv run pytest -q -p no:cacheprovider --cov=food-recipe-recommender/app --cov-report=term-missing

# Frontend
test-frontend:
	cd food-recipe-recommender/app/frontend && npm run test

test-frontend-cov:
	cd food-recipe-recommender/app/frontend && npm run test:run

# Live integration against a running backend
# Usage:
#   make test-live                 # uses default API_BASE_URL (http://127.0.0.1:8080/api)
#   make test-live API=http://localhost:8080/api
API ?= http://127.0.0.1:8080/api
test-live:
	LIVE_API=1 API_BASE_URL=$(API) uv run pytest -q -p no:cacheprovider tests/test_integration_live.py

# Docker
IMAGE ?= recipe-recommender
TAG ?= latest

docker-build:
	docker build -t $(IMAGE):$(TAG) .

docker-run:
	# Use local .env if present; ensure PORT is set
	@if [ -f food-recipe-recommender/app/.env ]; then \
		docker run --rm -p 8080:8080 --env-file food-recipe-recommender/app/.env -e PORT=8080 $(IMAGE):$(TAG); \
	else \
		docker run --rm -p 8080:8080 -e PORT=8080 $(IMAGE):$(TAG); \
	fi

docker-push:
	# Requires registry login and IMAGE including registry, e.g., ghcr.io/user/repo:tag
	docker push $(IMAGE):$(TAG)
