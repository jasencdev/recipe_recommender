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
#   make test-live                 # uses default API_BASE_URL (http://127.0.0.1:5000/api)
#   make test-live API=http://localhost:5000/api
API ?= http://127.0.0.1:5000/api
test-live:
	LIVE_API=1 API_BASE_URL=$(API) uv run pytest -q -p no:cacheprovider tests/test_integration_live.py

