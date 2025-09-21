## Testing & QA

- Backend unit tests:
  - Run: `uv run pytest -q -p no:cacheprovider`
  - With coverage: `uv run pytest -q -p no:cacheprovider --cov=app --cov-report=term-missing`

- Frontend unit tests (Vitest):
  - From `food-recipe-recommender/app/frontend`: `npm run test` (watch) or `npm run test:run` (coverage/CI)

- Live integration tests (hit running backend):
  - Start the Flask server locally
  - Run: `LIVE_API=1 uv run pytest -q -p no:cacheprovider tests/test_integration_live.py`
  - Optional: override base URL, e.g. `API_BASE_URL=http://localhost:5000/api`

- Makefile shortcuts (from repo root):
  - `make test` — backend unit tests
  - `make test-cov` — backend tests with coverage
  - `make test-frontend` — frontend tests (watch)
  - `make test-frontend-cov` — frontend tests with coverage
  - `make test-live` — live integration tests (override API with `make test-live API=http://localhost:5000/api`)

- CI & Coverage:
  - GitHub Actions runs backend and frontend tests on pushes/PRs.
  - Codecov reports coverage with separate flags for backend and frontend (thresholds in `codecov.yml`).
