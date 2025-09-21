"""Compatibility shim for legacy imports.

Provides a module named `app` when the interpreter's sys.path points at this
directory itself (instead of the parent directory). Exposes the same public
API that tests and older code expect, delegating implementation to the
blueprint-based package (`__init__.py`).
"""

from __future__ import annotations

import os
from typing import Optional

# Load the real package implementation under a different module name
import importlib.util as _ilu
import sys as _sys
import os as _os

_pkg_dir = _os.path.dirname(__file__)
_init_path = _os.path.join(_pkg_dir, "__init__.py")
_spec = _ilu.spec_from_file_location("app_pkg", _init_path, submodule_search_locations=[_pkg_dir])
assert _spec and _spec.loader
app_pkg = _ilu.module_from_spec(_spec)
_sys.modules.setdefault("app_pkg", app_pkg)
_spec.loader.exec_module(app_pkg)  # type: ignore[attr-defined]

# Re-export common objects from the real package
db = app_pkg.db
User = app_pkg.User
SavedRecipe = app_pkg.SavedRecipe
PasswordResetToken = app_pkg.PasswordResetToken
PasswordResetRequestLog = app_pkg.PasswordResetRequestLog
parse_list_field = app_pkg.parse_list_field
rate_limit_counts_impl = app_pkg._rate_limit_counts_impl if hasattr(app_pkg, "_rate_limit_counts_impl") else app_pkg._rate_limit_counts  # type: ignore

# Environment-derived constants mirrored here so tests can patch them
RESEND_API_KEY: Optional[str] = os.getenv('RESEND_API_KEY')
EMAIL_FROM: str = os.getenv('EMAIL_FROM', 'Recipe Recommender <no-reply@example.com>')
FRONTEND_BASE_URL: str = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')
ENVIRONMENT: str = os.getenv('ENV', 'development')
ADMIN_TOKEN: Optional[str] = os.getenv('ADMIN_TOKEN')

try:
    import resend  # type: ignore
    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
    RESEND_AVAILABLE = True
except Exception:  # pragma: no cover
    resend = None  # type: ignore
    RESEND_AVAILABLE = False


def _require_admin() -> bool:
    from flask import request
    token = request.headers.get('X-Admin-Token')
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        return False
    return True


def _rate_limit_counts(email: Optional[str], ip: Optional[str]):
    # Bind LogModel to PasswordResetRequestLog
    return app_pkg._rate_limit_counts_impl(email, ip, PasswordResetRequestLog)  # type: ignore[attr-defined]


def send_password_reset_email(to_email: str, token: str) -> bool:
    import logging as _logging
    from flask import current_app

    logger = _logging.getLogger("password-reset")
    try:
        base_url = FRONTEND_BASE_URL or current_app.config.get('FRONTEND_BASE_URL', 'http://localhost:5173')
        reset_link = f"{base_url.rstrip('/')}/reset-password?token={token}"
        subject = "Reset your password"
        html = f"""
            <div style='font-family:Arial,sans-serif;font-size:16px;color:#111'>
              <p>Hello,</p>
              <p>We received a request to reset your password. Click the link below to set a new password. This link expires in 1 hour.</p>
              <p><a href='{reset_link}' style='color:#2563eb'>Reset your password</a></p>
              <p>If you didn't request this, you can safely ignore this email.</p>
              <p>— Recipe Recommender</p>
            </div>
        """
        text = (
            "Hello,\n\n"
            "We received a request to reset your password. Use the link below to set a new password (expires in 1 hour).\n\n"
            f"{reset_link}\n\n"
            "If you didn't request this, you can ignore this email.\n\n"
            "— Recipe Recommender\n"
        )

        if current_app:
            if RESEND_API_KEY is not None:
                current_app.config['RESEND_API_KEY'] = RESEND_API_KEY
            if EMAIL_FROM:
                current_app.config['EMAIL_FROM'] = EMAIL_FROM
            if FRONTEND_BASE_URL:
                current_app.config['FRONTEND_BASE_URL'] = FRONTEND_BASE_URL
            current_app.config['RESEND_AVAILABLE'] = bool(RESEND_AVAILABLE)

        if RESEND_API_KEY and RESEND_AVAILABLE and resend is not None:
            try:
                resend.api_key = RESEND_API_KEY
                resend.Emails.send({
                    "from": EMAIL_FROM,
                    "to": [to_email],
                    "subject": subject,
                    "html": html,
                    "text": text,
                })
                logger.info("[reset-email] sent via Resend | to=%s", to_email)
                return True
            except Exception as e:  # pragma: no cover
                logger.exception("[reset-email] Resend send failed | to=%s | error=%s", to_email, e)
                return False
        else:
            # Fallback to package implementation that uses current_app.config
            return app_pkg._send_password_reset_email_impl(to_email, token)  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover
        logger.exception("[reset-email] unexpected error preparing email (shim)")
        return False


# Create default app instance for legacy WSGI entry: app:app
app = app_pkg.create_app()

# Expose the factory for servers/CLIs that use factory-mode (e.g., Waitress --call, Flask --app app:create_app)
def create_app():  # pragma: no cover
    return app_pkg.create_app()
