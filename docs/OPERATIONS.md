Operations: Email, Rate Limits, Admin Endpoints

Environment variables
- ENV: Set to `production` to disable dev shortcuts and send real emails.
- RESEND_API_KEY: API key for Resend.
- EMAIL_FROM: Verified sender (domain or address) in your Resend project.
- FRONTEND_BASE_URL: Base URL used for reset links.
- ADMIN_TOKEN: Shared secret required in `X-Admin-Token` header for admin endpoints.
- RATE_LIMIT_PER_IP_PER_HOUR: Default 5; used for forgot-password IP throttling.
- RATE_LIMIT_PER_EMAIL_PER_HOUR: Default 3; used for per-email throttling.
 - DATABASE_URL: Preferred. Use a managed Postgres URL in production.
 - SQLITE_DIR: Optional. Directory for a persistent SQLite file (e.g., `/data` on Railway volume). If unset and DATABASE_URL is empty, the app uses an in-container SQLite file (ephemeral).

Starting the server
- Local: `uv run flask --app app:create_app run --port 8080`
- Waitress (factory): `uv run waitress-serve --listen=127.0.0.1:8080 --call 'app:create_app'`
- Docker: `make docker-build && make docker-run`

Model artifact
- Expected path in image: `/app/food-recipe-recommender/models/recipe_recommender_model.joblib`.
- Ensure the file exists under `food-recipe-recommender/models/` before building.
- To mount a model at runtime, set `MODEL_PATH=/models/model.joblib` and bind mount the file into the container.

Database persistence (Railway)
- Recommended: Add a PostgreSQL service in Railway and set `DATABASE_URL` on the app.
- Alternative: Create a Railway Volume and mount at `/data`. Set `SQLITE_DIR=/data` on the app. The app will create `/data/database.db` and persist across deploys.
- Warning: If neither `DATABASE_URL` nor `SQLITE_DIR` is set, the app uses an in-container SQLite file which is reset on each deploy.

Admin endpoints
- GET `/api/admin/status/email`
  - Returns: `resend_available`, `has_api_key`, `email_from`, `frontend_base_url`, `environment`.

- POST `/api/admin/test-email`
  - Body: `{ "to": "you@example.com" }`
  - Returns: `{ "success": true/false }`.

- GET `/api/admin/rate-limit?email=...&ip=...`
  - Returns counts for last hour and last 24h.

- POST `/api/admin/maintenance/clear-reset-data`
  - Body: `{ "days": 7 }`
  - Deletes old entries from PasswordResetRequestLog and PasswordResetToken.

Resend checklist
- Ensure `EMAIL_FROM` uses a verified sender or domain in Resend (e.g., no-reply@yourdomain).
- Ensure `RESEND_API_KEY` is set and valid in the running environment.
- Ensure outbound network is permitted from the server to Resend.
- In development, the forgot-password route may return a `devResetToken` if sending fails; set `ENV=production` for live sends.

Troubleshooting
- Check server logs for `[reset-email] sent via Resend` or failure messages.
- Use `/api/admin/test-email` to bypass user existence checks and verify connectivity/config.
