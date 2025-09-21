import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Tuple

from flask import Blueprint, Response, current_app, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from .. import db
from ..models import PasswordResetRequestLog, PasswordResetToken, User
import app as app_module  # type: ignore

auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger(__name__)


@auth_bp.post("/api/register")
def register() -> Tuple[Response, int]:
    data: Dict[str, Any] = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    email = data.get("email", "").strip()
    email_norm = email.lower()
    password = data.get("password", "").strip()
    full_name = data.get("full_name", "").strip()

    if not email or not password or not full_name:
        return jsonify(
            {"success": False, "message": "Email, password, and full name are required"}
        ), 400

    # Keep lenient password requirements to match previous behavior/tests
    try:
        db.create_all()
        # Block duplicates regardless of casing
        if User.query.filter(func.lower(User.email_address) == email_norm).first():
            logger.debug(
                "[register] attempt with existing email | email=%s", email_norm[:2] + "***"
            )
            return jsonify({"success": False, "message": "Email already registered"}), 400

        user = User(
            # Store normalized lower-case email for consistency
            email_address=email_norm,
            full_name=full_name,
            country=data.get("country"),
            newsletter_signup=data.get("newsletter_signup", False),
        )
        user.password_hash = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)

        logger.info("[register] successful registration | user_id=%s", user.user_id)
        return jsonify({"success": True, "message": "Account created successfully"})
    except Exception as e:
        db.session.rollback()
        logger.error("[register] failed | reason=%s", str(e))
        return jsonify({"success": False, "message": "Registration failed"}), 500


@auth_bp.route("/api/login", methods=["GET", "POST"])
def login() -> Tuple[Response, int]:
    if request.method == "GET":
        return jsonify({"message": "Login required", "login_url": "/login"}), 401
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400
    submitted_email = (data.get("email") or "").strip().lower()
    user = User.query.filter(func.lower(User.email_address) == submitted_email).first()
    if user and check_password_hash(user.password_hash, data.get("password", "")):
        login_user(user)
        return jsonify({"success": True, "user": user.email_address})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401


@auth_bp.get("/api/auth/me")
def auth_me() -> Tuple[Response, int]:
    if current_user.is_authenticated:
        return jsonify(
            {
                "authenticated": True,
                "user": {"id": current_user.user_id, "email": current_user.email_address},
            }
        )
    return jsonify({"authenticated": False}), 401


@auth_bp.post("/api/logout")
@login_required
def logout() -> Response:
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})


@auth_bp.post("/api/forgot-password")
def forgot_password():
    try:
        data = request.get_json() or {}
        import secrets as _secrets

        rid = _secrets.token_hex(4)
        email = (data.get("email") or "").strip()
        email_norm = email.lower()
        # Use access_route (considering ProxyFix) for client IP
        try:
            ip_candidates = request.access_route or []
            ip = (ip_candidates[0] if ip_candidates else (request.remote_addr or "")).strip()
        except Exception:
            ip = (
                (request.headers.get("X-Forwarded-For") or request.remote_addr or "")
                .split(",")[0]
                .strip()
            )
        logger.debug("[forgot] rid=%s start | ip=%s | email=%s", rid, ip, email_norm[:2] + "***")
        generic_response = jsonify(
            {"success": True, "message": "If that email exists, a reset link has been sent."}
        )
        window_start = datetime.utcnow() - timedelta(hours=1)
        try:
            ip_count = PasswordResetRequestLog.query.filter(
                PasswordResetRequestLog.ip == ip, PasswordResetRequestLog.created_at >= window_start
            ).count()
        except Exception:
            ip_count = 0
        if ip and ip_count >= int(current_app.config.get("RATE_LIMIT_PER_IP_PER_HOUR", 5)):
            return generic_response
        if not email:
            try:
                db.session.add(PasswordResetRequestLog(email=None, ip=ip))
                db.session.commit()
            except Exception:
                db.session.rollback()
            return generic_response
        # Case-insensitive lookup for existing users
        user = User.query.filter(func.lower(User.email_address) == email_norm).first()
        if not user:
            try:
                db.session.add(PasswordResetRequestLog(email=email_norm, ip=ip))
                db.session.commit()
            except Exception:
                db.session.rollback()
            return generic_response
        try:
            email_count = PasswordResetRequestLog.query.filter(
                PasswordResetRequestLog.email == email_norm,
                PasswordResetRequestLog.created_at >= window_start,
            ).count()
        except Exception:
            email_count = 0
        if email_count >= int(current_app.config.get("RATE_LIMIT_PER_EMAIL_PER_HOUR", 3)):
            try:
                db.session.add(PasswordResetRequestLog(email=email_norm, ip=ip))
                db.session.commit()
            except Exception:
                db.session.rollback()
            return generic_response
        import secrets

        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        PasswordResetToken.query.filter_by(user_id=user.user_id, used=False).delete()
        reset_token = PasswordResetToken(
            user_id=user.user_id, token=raw_token, expires_at=expires_at
        )
        db.session.add(reset_token)
        db.session.commit()
        try:
            db.session.add(PasswordResetRequestLog(email=email_norm, ip=ip))
            db.session.commit()
        except Exception:
            db.session.rollback()
        email_sent = app_module.send_password_reset_email(user.email_address, raw_token)
        if not email_sent and current_app.config.get("ENVIRONMENT") != "production":
            return jsonify(
                {
                    "success": True,
                    "message": "Password reset link generated (development mode).",
                    "devResetToken": raw_token,
                }
            )
        return generic_response
    except Exception:
        db.session.rollback()
        return jsonify(
            {"success": True, "message": "If that email exists, a reset link has been sent."}
        )


@auth_bp.post("/api/reset-password")
def reset_password():
    try:
        data = request.get_json() or {}
        token = (data.get("token") or "").strip()
        new_password = (data.get("password") or "").strip()
        if not token or not new_password:
            return jsonify({"success": False, "message": "Invalid request"}), 400
        prt = PasswordResetToken.query.filter_by(token=token, used=False).first()
        if not prt or prt.expires_at < datetime.utcnow():
            return jsonify({"success": False, "message": "Invalid or expired token"}), 400
        user = db.session.get(User, prt.user_id)
        if not user:
            return jsonify({"success": False, "message": "Invalid token"}), 400
        user.password_hash = generate_password_hash(new_password)
        prt.used = True
        db.session.commit()
        return jsonify({"success": True, "message": "Password has been reset"})
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Password reset failed"}), 500
