## Running The App

- Development (factory):
  - From `food-recipe-recommender/app`: `uv run flask --app app:create_app run --port 8080`
  - The WSGI app is `app:create_app`; use `--call` with Waitress/Gunicorn factory modes.

- Docker:
  - Build: `make docker-build`
  - Run: `make docker-run` (loads `food-recipe-recommender/app/.env` if present)
  - Container entrypoint serves `--call 'app:create_app'` via Waitress.
  - Model: ensure `food-recipe-recommender/models/recipe_recommender_model.joblib` exists in the repo before building.
    - Alternatively, mount and override path:
      `docker run -p 8080:8080 -e PORT=8080 -e MODEL_PATH=/models/model.joblib -v /abs/path/to/model.joblib:/models/model.joblib:ro IMAGE:TAG`
  - Database persistence on Railway:
    - Recommended: attach a PostgreSQL service and set `DATABASE_URL`.
    - Or attach a Volume mounted at `/data` and set `SQLITE_DIR=/data` to persist SQLite across deploys.

- Admin endpoints (require `X-Admin-Token`):
  - Status: `GET /api/admin/status/email`
  - Test email: `POST /api/admin/test-email` body `{ "to": "you@example.com" }`
  - Rate limit inspect: `GET /api/admin/rate-limit?email=...&ip=...`
  - Cleanup: `POST /api/admin/maintenance/clear-reset-data` body `{ "days": 7 }`

## Testing & QA

- Backend unit tests:
  - Run: `uv run pytest -q -p no:cacheprovider`
  - With coverage: `uv run pytest -q -p no:cacheprovider --cov=food-recipe-recommender/app --cov-report=term-missing`

- Frontend unit tests (Vitest):
  - From `food-recipe-recommender/app/frontend`: `npm run test` (watch) or `npm run test:run` (coverage/CI)

- Live integration tests (hit running backend):
  - Start the Flask server locally
  - Run: `LIVE_API=1 uv run pytest -q -p no:cacheprovider tests/test_integration_live.py`
  - Optional: override base URL, e.g. `API_BASE_URL=http://localhost:8080/api`

- Makefile shortcuts (from repo root):
  - `make test` — backend unit tests
  - `make test-cov` — backend tests with coverage
  - `make test-frontend` — frontend tests (watch)
  - `make test-frontend-cov` — frontend tests with coverage
  - `make test-live` — live integration tests (override API with `make test-live API=http://localhost:8080/api`)

- CI & Coverage:
  - GitHub Actions runs backend and frontend tests on pushes/PRs.
  - Codecov reports coverage with separate flags for backend and frontend (thresholds in `codecov.yml`).

## Environment

- Place local settings in `food-recipe-recommender/app/.env` (auto-loaded in dev):
  - `SECRET_KEY`, `DATABASE_URL`, `ADMIN_TOKEN`
  - `RESEND_API_KEY`, `EMAIL_FROM`, `FRONTEND_BASE_URL`
  - `RATE_LIMIT_PER_IP_PER_HOUR`, `RATE_LIMIT_PER_EMAIL_PER_HOUR`

For Resend operations and admin endpoints, see `docs/OPERATIONS.md`.
