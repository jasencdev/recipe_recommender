import logging
import os

import joblib
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

try:
    from flask_wtf import CSRFProtect  # optional
except Exception:
    CSRFProtect = None  # type: ignore
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

# Internal singletons/flags to avoid repeated heavy loads
_RECOMMENDER_SINGLETON = None  # type: ignore[var-annotated]
_MODEL_PATH_PREPARED = False

db = SQLAlchemy()
login_manager = LoginManager()


def _prepare_model_imports(app_logger: logging.Logger) -> None:
    """Ensure the 'modules' package (data-pipeline) is importable for joblib unpickling.
    Prefer installed package via pyproject. Fallback: dynamic package loader without sys.path.
    """
    global _MODEL_PATH_PREPARED
    if _MODEL_PATH_PREPARED:
        return
    try:
        import modules  # type: ignore  # noqa: F401

        _MODEL_PATH_PREPARED = True
        return
    except Exception:
        pass
    try:
        # Fallback: register a runtime package named 'modules' pointing at data-pipeline/modules
        import importlib.util as _ilu
        import sys as _sys

        base_dir = os.path.dirname(__file__)
        pkg_dir = os.path.abspath(os.path.join(base_dir, "..", "data-pipeline", "modules"))
        init_path = os.path.join(pkg_dir, "__init__.py")
        spec = _ilu.spec_from_file_location(
            "modules", init_path, submodule_search_locations=[pkg_dir]
        )
        if spec and spec.loader:
            mod = _ilu.module_from_spec(spec)
            _sys.modules.setdefault("modules", mod)
            spec.loader.exec_module(mod)  # type: ignore[attr-defined]
            app_logger.info("[startup] loaded 'modules' package via fallback loader")
            _MODEL_PATH_PREPARED = True
    except Exception:
        # Let downstream loading fail cleanly; recommender will be None
        pass


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")
    CORS(app, supports_credentials=True)

    # Config and env
    # Load environment variables from the app's .env file (useful for local dev)
    try:
        base_dir = os.path.dirname(__file__)
        env_path = os.path.join(base_dir, ".env")
        load_dotenv(env_path)
    except Exception:
        # Fall back to default lookup if path-based load fails
        try:
            load_dotenv()
        except Exception:
            pass
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["ENVIRONMENT"] = os.getenv("ENV", "development")
    app.config["ADMIN_TOKEN"] = os.getenv("ADMIN_TOKEN")
    app.config["RESEND_API_KEY"] = os.getenv("RESEND_API_KEY")
    app.config["EMAIL_FROM"] = os.getenv("EMAIL_FROM", "Recipe Recommender <no-reply@example.com>")
    app.config["FRONTEND_BASE_URL"] = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
    app.config["RATE_LIMIT_PER_IP_PER_HOUR"] = int(
        os.getenv("RATE_LIMIT_PER_IP_PER_HOUR", "5").strip('"')
    )
    app.config["RATE_LIMIT_PER_EMAIL_PER_HOUR"] = int(
        os.getenv("RATE_LIMIT_PER_EMAIL_PER_HOUR", "3").strip('"')
    )

    # Configure Resend availability for email sending
    try:
        import resend  # type: ignore

        api_key = app.config.get("RESEND_API_KEY")
        if api_key:
            resend.api_key = api_key
        app.config["RESEND_AVAILABLE"] = bool(api_key)
    except Exception:
        # Either import failed or other issue; disable email sending
        app.config["RESEND_AVAILABLE"] = False

    # Logging
    _log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, _log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app_logger = logging.getLogger("app")

    # Database URL with fallback
    _db_url_env = (os.getenv("DATABASE_URL") or "").strip()
    if not _db_url_env:
        # Prefer a persistent directory if present (e.g., Railway volume mounted at /data)
        persistent_dir = (os.getenv("SQLITE_DIR") or "").strip() or (
            "/data" if os.path.isdir("/data") else ""
        )
        if persistent_dir:
            _db_path = os.path.join(persistent_dir, "database.db")
        else:
            _db_path = os.path.join(os.path.dirname(__file__), "instance", "database.db")
        try:
            os.makedirs(os.path.dirname(_db_path), exist_ok=True)
        except Exception:
            pass
        _db_url = f"sqlite:///{_db_path}"
        # Warn if likely ephemeral storage in production
        if app.config.get("ENVIRONMENT") == "production" and not persistent_dir:
            logging.getLogger("app").warning(
                "[startup] Using SQLite fallback at %s; data will be ephemeral. Set DATABASE_URL or SQLITE_DIR (e.g., /data with a persistent volume).",
                _db_path,
            )
    else:
        try:
            make_url(_db_url_env)
            _db_url = _db_url_env
        except Exception:
            _db_path = os.path.join(os.path.dirname(__file__), "instance", "database.db")
            try:
                os.makedirs(os.path.dirname(_db_path), exist_ok=True)
            except Exception:
                pass
            _db_url = f"sqlite:///{_db_path}"
    app.config["SQLALCHEMY_DATABASE_URI"] = _db_url

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "/login"

    # Optional CSRF for cookie-based sessions (disabled by default)
    try:
        # Default off for tests/dev unless explicitly enabled
        enable_csrf = os.getenv("ENABLE_CSRF", "false").lower() in {"1", "true"}
        if enable_csrf and CSRFProtect is not None:
            CSRFProtect(app)
            app_logger.info("[startup] CSRFProtect enabled")
    except Exception:
        pass

    # Proxy fix for correct IP/headers when behind reverse proxy (optional)
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix

        if (os.getenv("TRUST_PROXY", "false").lower() in {"1", "true"}) or app.config.get(
            "ENVIRONMENT"
        ) == "production":
            app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)  # type: ignore[attr-defined]
            app_logger.info("[startup] ProxyFix enabled")
    except Exception:
        pass

    # Load recommender model (supports override via MODEL_PATH) with singleton cache
    global _RECOMMENDER_SINGLETON
    try:
        _prepare_model_imports(app_logger)
        base_dir = os.path.dirname(__file__)
        model_path = os.getenv("MODEL_PATH") or os.path.abspath(
            os.path.join(base_dir, "..", "models", "recipe_recommender_model.joblib")
        )
        if _RECOMMENDER_SINGLETON is None:
            app_logger.info("[startup] loading recommender | path=%s", model_path)
            _RECOMMENDER_SINGLETON = joblib.load(model_path)
            app_logger.info("[startup] recommender loaded")
        else:
            app_logger.info("[startup] recommender cached; reusing singleton")
        app.config["RECOMMENDER"] = _RECOMMENDER_SINGLETON
    except Exception as _e:
        app_logger.warning("[startup] recommender unavailable | reason=%s", getattr(_e, "args", _e))
        app.config["RECOMMENDER"] = None

    # Models and user loader

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # Blueprints
    from .blueprints.admin import admin_bp
    from .blueprints.auth import auth_bp
    from .blueprints.misc import misc_bp
    from .blueprints.recipes import recipes_bp
    from .blueprints.saved import saved_bp

    app.register_blueprint(misc_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(saved_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(admin_bp)

    # Idempotent DB init for dev/SQLite
    try:
        with app.app_context():
            db.create_all()
            # One-time lightweight schema migration for password_hash length on Postgres
            try:
                from sqlalchemy import text

                uri = (app.config.get("SQLALCHEMY_DATABASE_URI") or "").lower()
                if uri.startswith("postgres"):  # postgres or postgresql
                    with db.engine.begin() as conn:  # type: ignore[attr-defined]
                        current_len = conn.execute(
                            text(
                                """
                            SELECT character_maximum_length
                            FROM information_schema.columns
                            WHERE table_name = 'user' AND column_name = 'password_hash'
                            """
                            )
                        ).scalar()
                        if current_len is not None and int(current_len) < 200:
                            conn.execute(
                                text(
                                    'ALTER TABLE "user" ALTER COLUMN password_hash TYPE VARCHAR(255)'
                                )
                            )
                            logging.getLogger("app").info(
                                "[startup] migrated password_hash to VARCHAR(255)"
                            )
                        # Ensure a case-insensitive unique index on email_address
                        conn.execute(
                            text(
                                'CREATE UNIQUE INDEX IF NOT EXISTS uq_user_email_lower ON "user" (lower(email_address))'
                            )
                        )
            except Exception:
                # Best-effort migration; ignore if it fails
                pass
    except Exception:
        pass

    # Static assets and SPA handling
    @app.route("/assets/<path:filename>")
    def vite_assets(filename):
        assets_dir = os.path.join(app.root_path, "static", "assets")
        return send_from_directory(assets_dir, filename)

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/login")
    def login_page():
        return render_template("index.html")

    @app.errorhandler(500)
    def api_json_500(e):
        p = request.path or ""
        if p.startswith("/api"):
            return jsonify({"error": "Internal server error"}), 500
        return e

    @app.errorhandler(404)
    def spa_fallback(e):
        path = request.path.lstrip("/")
        if path.startswith("api") or path.startswith("assets") or path.startswith("static"):
            return e
        return render_template("index.html")

    # CSRF token issuer for SPA
    try:
        from flask_wtf.csrf import generate_csrf  # type: ignore

        @app.get("/api/csrf")
        def get_csrf_token():
            token = generate_csrf()
            resp = jsonify({"csrfToken": token})
            resp.set_cookie(
                "csrf_token",
                token,
                secure=app.config.get("ENVIRONMENT") == "production",
                httponly=False,  # JS must read it
                samesite="Lax",
            )
            return resp
    except Exception:
        pass

    return app


# ---------------------------------------------------------------------------------
# Backwards-compat exports and helpers to keep legacy imports/tests working
# ---------------------------------------------------------------------------------

# Expose models at package level
from .models import PasswordResetRequestLog, PasswordResetToken, SavedRecipe, User  # noqa: E402

# Module-level env-derived constants (for legacy patches in tests)
RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY")
EMAIL_FROM: str = os.getenv("EMAIL_FROM", "Recipe Recommender <no-reply@example.com>")
FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
ENVIRONMENT: str = os.getenv("ENV", "development")
ADMIN_TOKEN: Optional[str] = os.getenv("ADMIN_TOKEN")

try:
    import resend  # type: ignore

    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
        RESEND_AVAILABLE = True
    else:
        RESEND_AVAILABLE = False
except Exception:  # pragma: no cover
    resend = None  # type: ignore
    RESEND_AVAILABLE = False

# Re-export selected utils and provide legacy-named wrappers
from .utils import parse_list_field  # noqa: E402
from .utils import rate_limit_counts as _rate_limit_counts_impl  # noqa: E402
from .utils import require_admin as _require_admin_impl  # noqa: E402
from .utils import send_password_reset_email as _send_password_reset_email_impl  # noqa: E402


def _require_admin() -> bool:
    """Legacy-compatible admin check delegating to utils.require_admin.
    Maintains legacy import path while using single-source implementation.
    """
    return _require_admin_impl()


def _rate_limit_counts(email: Optional[str], ip: Optional[str]):
    """Legacy wrapper that binds LogModel to PasswordResetRequestLog."""
    return _rate_limit_counts_impl(email, ip, PasswordResetRequestLog)


def send_password_reset_email(to_email: str, token: str) -> bool:
    """Legacy-compatible email sender that respects module-level patches.
    Tests patch app.RESEND_API_KEY, app.RESEND_AVAILABLE, app.EMAIL_FROM, app.FRONTEND_BASE_URL,
    and app.resend. This wrapper reads those and orchestrates the send accordingly.
    """
    import logging as _logging
    from flask import current_app

    logger = _logging.getLogger("password-reset")
    try:
        # Build content based on module-level FRONTEND_BASE_URL
        base_url = FRONTEND_BASE_URL or current_app.config.get(
            "FRONTEND_BASE_URL", "http://localhost:5173"
        )
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

        # Ensure current_app.config reflects module-level patches for consistency
        if current_app:  # pragma: no branch
            if RESEND_API_KEY is not None:
                current_app.config["RESEND_API_KEY"] = RESEND_API_KEY
            if EMAIL_FROM:
                current_app.config["EMAIL_FROM"] = EMAIL_FROM
            if FRONTEND_BASE_URL:
                current_app.config["FRONTEND_BASE_URL"] = FRONTEND_BASE_URL
            current_app.config["RESEND_AVAILABLE"] = bool(RESEND_AVAILABLE)

        if RESEND_API_KEY and RESEND_AVAILABLE and resend is not None:
            try:
                resend.api_key = RESEND_API_KEY
                resend.Emails.send(
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
            except Exception as e:  # pragma: no cover
                logger.exception(
                    "[reset-email] Resend send failed | to=%s | error=%s", to_email, e
                )
                return False
        else:
            # Fall back to the utils implementation (uses current_app.config)
            return _send_password_reset_email_impl(to_email, token)
    except Exception:  # pragma: no cover
        logger = _logging.getLogger("password-reset")
        logger.exception("[reset-email] unexpected error preparing email (wrapper)")
        return False


# Create a default app instance to preserve legacy imports only in test/CI
if os.getenv("ENV", "development").lower() in {"test", "ci"}:
    app = create_app()  # type: ignore[assignment]
