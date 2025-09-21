import json
import logging
from datetime import datetime, timedelta
from typing import Any, List, Optional, Type

from flask import current_app, request
from flask_sqlalchemy.model import Model


def parse_list_field(raw_data: Any, fallback_split: str = ",") -> List[str]:
    """Parse list-like fields that may be stored as actual lists, JSON strings, or Python list reprs.
    Returns a list[str] with surrounding quotes/brackets stripped and empty items removed.
    """
    try:
        if isinstance(raw_data, list):
            return [str(x).strip() for x in raw_data if str(x).strip()]
        if not isinstance(raw_data, str) or not raw_data.strip():
            return []
        s = raw_data.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception as e:
                logging.getLogger("utils").debug("json loads failed: %s", e)
            try:
                import ast

                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception as e:
                logging.getLogger("utils").debug("ast parse failed: %s", e)
        items = []
        for item in s.split(fallback_split):
            cleaned = item.strip().strip("[]'").strip('"')
            if cleaned:
                items.append(cleaned)
        return items
    except Exception as e:
        logging.getLogger("utils").debug("parse_list_field failed: %s", e)
        return []


def send_password_reset_email(to_email: str, token: str) -> bool:
    logger = logging.getLogger("password-reset")
    FRONTEND_BASE_URL = current_app.config.get("FRONTEND_BASE_URL", "http://localhost:5173")
    RESEND_API_KEY = current_app.config.get("RESEND_API_KEY")
    EMAIL_FROM = current_app.config.get("EMAIL_FROM", "Recipe Recommender <no-reply@example.com>")
    # ENVIRONMENT not directly used; relies on app config elsewhere

    try:
        reset_link = f"{FRONTEND_BASE_URL.rstrip('/')}/reset-password?token={token}"
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
        if RESEND_API_KEY and current_app.config.get("RESEND_AVAILABLE"):
            try:
                # Prefer app.resend mock if available (tests patch this), else import library
                try:
                    import app as app_module  # type: ignore
                    resend_client = getattr(app_module, "resend", None)
                except Exception:
                    resend_client = None
                if resend_client is None:
                    import resend as resend_client  # type: ignore

                resend_client.api_key = RESEND_API_KEY
                resend_client.Emails.send(
                    {
                        "from": EMAIL_FROM,
                        "to": [to_email],
                        "subject": subject,
                        "html": html,
                        "text": text,
                    }
                )
                logger.info("[reset-email] sent via Resend | to=%s", to_email)
                return True
            except Exception as e:
                logger.exception("[reset-email] Resend send failed | to=%s | error=%s", to_email, e)
                return False
        else:
            # Avoid leaking full email addresses at info level
            redacted = _redact_email(to_email)
            logger.debug("[reset-email] sending disabled | to=%s | link=%s", redacted, reset_link)
            return False
    except Exception:
        logger.exception("[reset-email] unexpected error preparing email")
        return False


def _redact_email(email: str) -> str:
    try:
        local, _, domain = email.partition("@")
        if not local or not domain:
            return "***"
        return local[:2] + "***@" + domain
    except Exception:
        return "***"


def require_admin() -> bool:
    """Check if the current request has a valid admin token.
    Accepts either current_app.config['ADMIN_TOKEN'] or module-level app.ADMIN_TOKEN (legacy tests).
    """
    token = request.headers.get("X-Admin-Token")
    # Candidate 1: from app config
    cfg_token = current_app.config.get("ADMIN_TOKEN")
    # Candidate 2: module-level shim value
    try:
        import app as app_module  # type: ignore

        mod_token = getattr(app_module, "ADMIN_TOKEN", None)
    except Exception:
        mod_token = None
    for cand in (cfg_token, mod_token):
        if cand and token == cand:
            return True
    return False


def rate_limit_counts(
    email: Optional[str], ip: Optional[str], LogModel: Type[Model]
) -> dict[str, dict[str, int]]:
    now = datetime.utcnow()
    window_1h = now - timedelta(hours=1)
    window_24h = now - timedelta(hours=24)
    counts = {"ip": {"last_hour": 0, "last_24h": 0}, "email": {"last_hour": 0, "last_24h": 0}}
    try:
        if ip:
            counts["ip"]["last_hour"] = LogModel.query.filter(
                LogModel.ip == ip,
                LogModel.created_at >= window_1h,
            ).count()
            counts["ip"]["last_24h"] = LogModel.query.filter(
                LogModel.ip == ip,
                LogModel.created_at >= window_24h,
            ).count()
        if email:
            email_norm = email.lower()
            counts["email"]["last_hour"] = LogModel.query.filter(
                LogModel.email == email_norm,
                LogModel.created_at >= window_1h,
            ).count()
            counts["email"]["last_24h"] = LogModel.query.filter(
                LogModel.email == email_norm,
                LogModel.created_at >= window_24h,
            ).count()
    except Exception as e:
        logging.getLogger("utils").debug("rate_limit_counts query failed: %s", e)
    return counts
