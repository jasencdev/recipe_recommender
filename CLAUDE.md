# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend Testing
- `uv run pytest -q -p no:cacheprovider` - Run backend unit tests
- `uv run pytest -q -p no:cacheprovider --cov=food-recipe-recommender/app --cov-report=term-missing` - Run with coverage
- `LIVE_API=1 uv run pytest -q -p no:cacheprovider tests/test_integration_live.py` - Live integration tests against running backend

### Frontend Testing
- From `food-recipe-recommender/app/frontend/`: `npm run test` (watch mode) or `npm run test:run` (coverage/CI)

### Makefile Shortcuts
- `make test` - Backend unit tests
- `make test-cov` - Backend tests with coverage
- `make test-frontend` - Frontend tests (watch)
- `make test-frontend-cov` - Frontend tests with coverage
- `make test-live` - Live integration tests (override API with `make test-live API=http://localhost:5000/api`)

### Build and Development
- Frontend build: `cd food-recipe-recommender/app/frontend && npm run build`
- Frontend dev server: `cd food-recipe-recommender/app/frontend && npm run dev`
- Docker build: `make docker-build`
- Docker run: `make docker-run`

## Architecture Overview

### Project Structure
This is a Flask-based recipe recommendation system with a React frontend:

```
food-recipe-recommender/
├── app/                          # Flask application
│   ├── __init__.py              # App factory with Flask, CORS, SQLAlchemy setup
│   ├── models.py                # SQLAlchemy models (User, SavedRecipe, PasswordResetToken)
│   ├── utils.py                 # Utility functions
│   ├── blueprints/              # Flask blueprints for API routes
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── recipes.py           # Recipe search/recommendation endpoints
│   │   ├── saved.py             # Saved recipes management
│   │   └── misc.py              # Miscellaneous endpoints
│   ├── frontend/                # React/TypeScript SPA
│   ├── templates/               # Flask templates (serves built React app)
│   └── static/                  # Static assets
├── data/                        # Datasets (not in Git)
├── data-pipeline/               # Data processing scripts
└── models/                      # ML model artifacts
```

### Key Components

**Flask App Factory**: `food-recipe-recommender/app/__init__.py`
- Configures Flask with CORS, SQLAlchemy, Flask-Login
- Loads ML recommender model from `../models/recipe_recommender_model.joblib`
- Registers blueprints for modular API structure
- Handles SPA routing fallback for React frontend

**Database Models**: `food-recipe-recommender/app/models.py`
- `User` - User accounts with Flask-Login integration
- `SavedRecipe` - User's saved recipes
- `PasswordResetToken` - Password reset functionality
- `PasswordResetRequestLog` - Rate limiting for password resets

**API Blueprints**:
- `auth.py` - Login, registration, password reset with rate limiting
- `recipes.py` - Recipe search, recommendations, details
- `saved.py` - Save/unsave recipes functionality
- `misc.py` - Health checks and admin endpoints

**Frontend**: React/TypeScript SPA with Vite
- Uses Tailwind CSS, Headless UI, Heroicons
- Testing with Vitest and React Testing Library
- Builds to `dist/` and gets copied into Flask templates/static during Docker build

### ML Integration
- Recipe recommender model loaded at app startup from `models/recipe_recommender_model.joblib`
- Model available as `app.config['RECOMMENDER']` throughout the application
- Graceful degradation if model file not found

### Database
- SQLite for development (auto-created in `instance/database.db`)
- Supports PostgreSQL via `DATABASE_URL` environment variable
- Auto-creates tables on startup for development

### Authentication & Security
- Flask-Login for session management
- Rate limiting for password reset requests (IP and email based)
- CSRF protection with Flask-WTF
- Admin endpoints protected by `ADMIN_TOKEN`

### Environment Configuration
Key environment variables:
- `SECRET_KEY` - Flask session secret
- `DATABASE_URL` - Database connection string
- `RESEND_API_KEY` - Email service for password resets
- `ADMIN_TOKEN` - Admin API access
- `RATE_LIMIT_PER_IP_PER_HOUR` / `RATE_LIMIT_PER_EMAIL_PER_HOUR` - Rate limiting

### Deployment
- Multi-stage Docker build: builds React frontend, then packages Flask app
- Uses Waitress WSGI server in production
- Designed for Railway deployment with `PORT` environment variable
- Coverage reporting via Codecov with separate backend/frontend flags