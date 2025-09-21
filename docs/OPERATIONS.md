Operations: Email, Rate Limits, Admin Endpoints

Environment variables
- ENV: Set to `production` to disable dev shortcuts and send real emails.
- RESEND_API_KEY: API key for Resend.
- EMAIL_FROM: Verified sender (domain or address) in your Resend project.
- FRONTEND_BASE_URL: Base URL used for reset links.
- ADMIN_TOKEN: Shared secret required in `X-Admin-Token` header for admin endpoints.
- RATE_LIMIT_PER_IP_PER_HOUR: Default 5; used for forgot-password IP throttling.
- RATE_LIMIT_PER_EMAIL_PER_HOUR: Default 3; used for per-email throttling.

Starting the server
- Local: `uv run flask --app app:create_app run --port 8080`
- Docker: `make docker-build && make docker-run`

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

