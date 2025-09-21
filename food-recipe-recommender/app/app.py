'''Simple Flask application for a food recipe recommender.'''
import os
import joblib
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, session, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import make_url
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import logging

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') # Change this to a random secret key in production
CORS(app, supports_credentials=True)  # Allow cookies in CORS requests

# Resolve SQLALCHEMY_DATABASE_URI with safe fallback
_db_url_env = (os.getenv('DATABASE_URL') or '').strip()
if not _db_url_env:
    # Default to a local SQLite file inside the app instance directory
    _db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
    os.makedirs(os.path.dirname(_db_path), exist_ok=True)
    _db_url = f'sqlite:///{_db_path}'
else:
    try:
        # Validate URL; if invalid, fall back to SQLite file
        make_url(_db_url_env)
        _db_url = _db_url_env
    except Exception:
        _db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
        os.makedirs(os.path.dirname(_db_path), exist_ok=True)
        _db_url = f'sqlite:///{_db_path}'

app.config['SQLALCHEMY_DATABASE_URI'] = _db_url
db = SQLAlchemy(app)

# Email / Resend configuration and logging
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'Recipe Recommender <no-reply@example.com>')
FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')
ENVIRONMENT = os.getenv('ENV', 'development')
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')

# Rate limiting configuration
RATE_LIMIT_PER_IP_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_IP_PER_HOUR', '5'))
RATE_LIMIT_PER_EMAIL_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_EMAIL_PER_HOUR', '3'))

try:
    import resend  # type: ignore
    if RESEND_API_KEY:
        resend.api_key = RESEND_API_KEY
    RESEND_AVAILABLE = True
except Exception:
    RESEND_AVAILABLE = False

# Structured logging configuration
# LOG_LEVEL can be set to DEBUG, INFO, WARNING, ERROR, CRITICAL
_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, _log_level, logging.INFO),
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger("password-reset")
app_logger = logging.getLogger("app")

# Load ML models (robust path + aliasing for pickled modules)
try:
    import sys as _sys
    import os as _os
    base_dir = _os.path.dirname(__file__)
    data_pipeline_dir = _os.path.abspath(_os.path.join(base_dir, '..', 'data-pipeline'))
    if data_pipeline_dir not in _sys.path:
        _sys.path.append(data_pipeline_dir)

    model_path = _os.path.abspath(_os.path.join(base_dir, '..', 'models', 'recipe_recommender_model.joblib'))
    recipe_recommender = joblib.load(model_path)
except Exception as e:
    recipe_recommender = None

## Removed duplicate legacy ML model loader to avoid double loads and noisy errors

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
# Redirect to frontend login route served by this app (works in dev/prod)
login_manager.login_view = '/login'
login_manager.login_message = 'Please log in to access this page.'

# Database Models
class SavedRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipe_id = db.Column(db.String(50), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure a user can't save the same recipe twice
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe'),)

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    country = db.Column(db.String(50))
    newsletter_signup = db.Column(db.Boolean)

    # Flask-Login requirements
    def get_id(self):
        return str(self.user_id)  # Flask-Login expects string

    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email_address}>'

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class PasswordResetRequestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=True)
    ip = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# Routes
@login_manager.user_loader
def load_user(user_id):
    # In a real application, you would load the user from a database
    return db.session.get(User, int(user_id))

@app.route("/api/health", methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    # Validate required fields
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    
    if not email or not password or not full_name:
        return jsonify({'success': False, 'message': 'Email, password, and full name are required'}), 400
    
    # Create new user
    try:
        # Ensure DB schema exists (useful with SQLite fallback)
        db.create_all()

        # Check if user already exists
        if User.query.filter_by(email_address=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'}), 400

        user = User(
            email_address=email,
            full_name=full_name,
            country=data.get('country'),
            newsletter_signup=data.get('newsletter_signup', False)
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log user in immediately after registration
        login_user(user)
        
        return jsonify({
            'success': True, 
            'message': 'Account created successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Registration failed'}), 500

@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # For API, return JSON indicating login required
        return jsonify({
            'message': 'Login required', 
            'login_url': '/login'
        }), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
        
    user = authenticate_user(data.get('email'), data.get('password'))
    if user:
        login_user(user)
        return jsonify({'success': True, 'user': user.email_address})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/auth/me', methods=['GET'])
def auth_check():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.user_id,
                'email': current_user.email_address
            }
        })
    return jsonify({'authenticated': False}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

def authenticate_user(email, password):
    user = User.query.filter_by(email_address=email).first()
    if user and user.check_password(password):
        return user
    return None

# Utility: robust list parsing for ingredients/instructions
def parse_list_field(raw_data, fallback_split=','):
    """Parse list-like fields that may be stored as actual lists, JSON strings, or Python list reprs.
    Returns a list[str] with surrounding quotes/brackets stripped and empty items removed.
    """
    try:
        # Already a list
        if isinstance(raw_data, list):
            return [str(x).strip() for x in raw_data if str(x).strip()]

        # Nothing to parse
        if not isinstance(raw_data, str) or not raw_data.strip():
            return []

        s = raw_data.strip()

        # Try JSON first (requires double quotes)
        if s.startswith('[') and s.endswith(']'):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                # Fall through to Python literal parsing
                pass

            # Try Python literal list (handles single quotes)
            try:
                import ast
                parsed = ast.literal_eval(s)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass

        # Fallback: split by delimiter and strip common wrappers
        items = []
        for item in s.split(fallback_split):
            cleaned = item.strip().strip("[]'")
            cleaned = cleaned.strip().strip('"')
            if cleaned:
                items.append(cleaned)
        return items
    except Exception:
        return []

def send_password_reset_email(to_email: str, token: str) -> bool:
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
        if RESEND_API_KEY and RESEND_AVAILABLE:
            try:
                resend.Emails.send({
                    "from": EMAIL_FROM,
                    "to": [to_email],
                    "subject": subject,
                    "html": html,
                    "text": text,
                })
                logger.info("[reset-email] sent via Resend | to=%s", to_email)
                return True
            except Exception as e:
                logger.exception("[reset-email] Resend send failed | to=%s | error=%s", to_email, e)
                return False
        else:
            logger.info("[reset-email] sending disabled | to=%s | link=%s", to_email, reset_link)
            return False
    except Exception:
        logger.exception("[reset-email] unexpected error preparing email")
        return False

def _require_admin():
    token = request.headers.get('X-Admin-Token')
    if not ADMIN_TOKEN or token != ADMIN_TOKEN:
        return False
    return True

def _rate_limit_counts(email: str | None, ip: str | None):
    now = datetime.utcnow()
    window_1h = now - timedelta(hours=1)
    window_24h = now - timedelta(hours=24)
    counts = {"ip": {"last_hour": 0, "last_24h": 0}, "email": {"last_hour": 0, "last_24h": 0}}
    try:
        if ip:
            counts["ip"]["last_hour"] = PasswordResetRequestLog.query.filter(
                PasswordResetRequestLog.ip == ip,
                PasswordResetRequestLog.created_at >= window_1h,
            ).count()
            counts["ip"]["last_24h"] = PasswordResetRequestLog.query.filter(
                PasswordResetRequestLog.ip == ip,
                PasswordResetRequestLog.created_at >= window_24h,
            ).count()
        if email:
            email_norm = email.lower()
            counts["email"]["last_hour"] = PasswordResetRequestLog.query.filter(
                PasswordResetRequestLog.email == email_norm,
                PasswordResetRequestLog.created_at >= window_1h,
            ).count()
            counts["email"]["last_24h"] = PasswordResetRequestLog.query.filter(
                PasswordResetRequestLog.email == email_norm,
                PasswordResetRequestLog.created_at >= window_24h,
            ).count()
    except Exception:
        pass
    return counts

@app.route('/api/admin/status/email', methods=['GET'])
def admin_status_email():
    if not _require_admin():
        return jsonify({"error": "forbidden"}), 403
    return jsonify({
        "resend_available": RESEND_AVAILABLE,
        "has_api_key": bool(RESEND_API_KEY),
        "email_from": EMAIL_FROM,
        "frontend_base_url": FRONTEND_BASE_URL,
        "rate_limit": {
            "per_ip_per_hour": RATE_LIMIT_PER_IP_PER_HOUR,
            "per_email_per_hour": RATE_LIMIT_PER_EMAIL_PER_HOUR,
        },
        "environment": ENVIRONMENT,
    })

@app.route('/api/admin/rate-limit', methods=['GET'])
def admin_rate_limit_inspect():
    if not _require_admin():
        return jsonify({"error": "forbidden"}), 403
    email = request.args.get('email')
    ip = request.args.get('ip')
    return jsonify({
        "query": {"email": email, "ip": ip},
        "counts": _rate_limit_counts(email, ip),
    })

@app.route('/api/admin/maintenance/clear-reset-data', methods=['POST'])
def admin_clear_reset_data():
    if not _require_admin():
        return jsonify({"error": "forbidden"}), 403
    try:
        data = request.get_json(silent=True) or {}
        days = int(data.get('days', 7))
        cutoff = datetime.utcnow() - timedelta(days=days)

        logs_deleted = PasswordResetRequestLog.query.filter(
            PasswordResetRequestLog.created_at < cutoff
        ).delete()

        tokens_deleted = PasswordResetToken.query.filter(
            (PasswordResetToken.expires_at < cutoff) | (PasswordResetToken.created_at < cutoff)
        ).delete()

        db.session.commit()
        return jsonify({
            "success": True,
            "deleted": {"logs": logs_deleted, "tokens": tokens_deleted},
            "cutoff": cutoff.isoformat() + 'Z'
        })
    except Exception:
        db.session.rollback()
        return jsonify({"success": False, "message": "Cleanup failed"}), 500

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json() or {}
        import secrets as _secrets
        rid = _secrets.token_hex(4)
        email = (data.get('email') or '').strip()
        email_norm = email.lower()
        ip = (request.headers.get('X-Forwarded-For') or request.remote_addr or '').split(',')[0].strip()
        logger.info("[forgot] rid=%s start | ip=%s | email=%s", rid, ip, email_norm)

        generic_response = jsonify({
            'success': True,
            'message': 'If that email exists, a reset link has been sent.'
        })

        window_start = datetime.utcnow() - timedelta(hours=1)
        try:
            ip_count = PasswordResetRequestLog.query.filter(
                PasswordResetRequestLog.ip == ip,
                PasswordResetRequestLog.created_at >= window_start
            ).count()
        except Exception:
            ip_count = 0
        logger.info("[forgot] rid=%s rate-ip | ip=%s | count=%s/%s", rid, ip, ip_count, RATE_LIMIT_PER_IP_PER_HOUR)
        if ip and ip_count >= RATE_LIMIT_PER_IP_PER_HOUR:
            logger.warning("[forgot] rid=%s limit-hit ip | ip=%s", rid, ip)
            return generic_response

        if not email:
            try:
                db.session.add(PasswordResetRequestLog(email=None, ip=ip))
                db.session.commit()
            except Exception:
                db.session.rollback()
            logger.info("[forgot] rid=%s no-email-provided | ip=%s", rid, ip)
            return generic_response

        user = User.query.filter_by(email_address=email_norm).first()
        if not user:
            try:
                db.session.add(PasswordResetRequestLog(email=email_norm, ip=ip))
                db.session.commit()
            except Exception:
                db.session.rollback()
            logger.info("[forgot] rid=%s unknown-email | ip=%s | email=%s", rid, ip, email_norm)
            return generic_response

        try:
            email_count = PasswordResetRequestLog.query.filter(
                PasswordResetRequestLog.email == email_norm,
                PasswordResetRequestLog.created_at >= window_start
            ).count()
        except Exception:
            email_count = 0
        logger.info("[forgot] rid=%s rate-email | email=%s | count=%s/%s", rid, email_norm, email_count, RATE_LIMIT_PER_EMAIL_PER_HOUR)
        if email_count >= RATE_LIMIT_PER_EMAIL_PER_HOUR:
            try:
                db.session.add(PasswordResetRequestLog(email=email_norm, ip=ip))
                db.session.commit()
            except Exception:
                db.session.rollback()
            logger.warning("[forgot] rid=%s limit-hit email | ip=%s | email=%s", rid, ip, email_norm)
            return generic_response

        import secrets
        raw_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        PasswordResetToken.query.filter_by(user_id=user.user_id, used=False).delete()
        reset_token = PasswordResetToken(user_id=user.user_id, token=raw_token, expires_at=expires_at)
        db.session.add(reset_token)
        db.session.commit()
        logger.info("[forgot] rid=%s token-created | user_id=%s | expires_at=%s", rid, user.user_id, expires_at.isoformat() + 'Z')

        try:
            db.session.add(PasswordResetRequestLog(email=email_norm, ip=ip))
            db.session.commit()
        except Exception:
            db.session.rollback()
        logger.info("[forgot] rid=%s log-written | ip=%s | email=%s", rid, ip, email_norm)

        email_sent = send_password_reset_email(user.email_address, raw_token)
        logger.info("[forgot] rid=%s email-sent=%s | ip=%s | email=%s", rid, email_sent, ip, email_norm)
        if not email_sent and ENVIRONMENT != 'production':
            return jsonify({'success': True, 'message': 'Password reset link generated (development mode).', 'devResetToken': raw_token})

        return generic_response
    except Exception:
        db.session.rollback()
        return jsonify({'success': True, 'message': 'If that email exists, a reset link has been sent.'})

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json() or {}
        token = (data.get('token') or '').strip()
        new_password = (data.get('password') or '').strip()
        if not token or not new_password:
            return jsonify({'success': False, 'message': 'Invalid request'}), 400
        prt = PasswordResetToken.query.filter_by(token=token, used=False).first()
        if not prt or prt.expires_at < datetime.utcnow():
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 400
        user = db.session.get(User, prt.user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Invalid token'}), 400
        user.set_password(new_password)
        prt.used = True
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password has been reset'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Password reset failed'}), 500

# Recipe API endpoints
@app.route('/api/search', methods=['GET'])
def search_recipes():
    """Search recipes with filters and text query."""
    if not recipe_recommender:
        return jsonify({'error': 'Recipe recommendation service unavailable'}), 500

    # Get query parameters
    query = request.args.get('query', '')
    complexity_score = request.args.get('complexity_score', type=float)
    number_of_ingredients = request.args.get('number_of_ingredients', type=int)
    dietary_restrictions = request.args.get('dietary_restrictions', '')
    cuisine = request.args.get('cuisine', '')
    cook_time = request.args.get('cook_time', type=int)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    try:
        # Use the ML model for recommendations when complexity/cook time/ingredients are specified
        if complexity_score is not None or cook_time is not None or number_of_ingredients is not None:
            # Use model's recommendation engine
            desired_complexity = complexity_score if complexity_score is not None else 25  # Default complexity
            desired_time = cook_time if cook_time is not None else 30  # Default cook time
            desired_ingredients = number_of_ingredients if number_of_ingredients is not None else 10  # Default ingredients

            all_recipes = recipe_recommender.recommend_recipes(
                desired_time=desired_time,
                desired_complexity=desired_complexity,
                desired_ingredients=desired_ingredients,
                n_recommendations=1000  # Get many results to allow further filtering
            )
        elif query:
            # Use text search for query-based searches
            all_recipes = recipe_recommender.search_recipes(query, n_results=1000)
        else:
            # Default: return all recipes
            all_recipes = recipe_recommender.data.copy()

        # Apply additional filters on top of model results
        if cuisine:
            if 'cuisine' in all_recipes.columns:
                all_recipes = all_recipes[all_recipes['cuisine'].str.contains(cuisine, case=False, na=False)]

        # Apply dietary restrictions filter
        if dietary_restrictions:
            dietary_list = [d.strip() for d in dietary_restrictions.split(',')]
            for dietary in dietary_list:
                if 'dietary_tags' in all_recipes.columns:
                    all_recipes = all_recipes[all_recipes['dietary_tags'].str.contains(dietary, case=False, na=False)]

        # No need for manual ingredient filtering - the ML model handles this now

        # Calculate pagination
        total = len(all_recipes)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_recipes = all_recipes.iloc[start_idx:end_idx]

        # Convert to frontend format
        recipes = []
        for _, recipe in paginated_recipes.iterrows():
            try:
                # Handle different ways the data might be stored
                recipe_id = str(recipe.get('food_recipe_id', recipe.get('id', recipe.name)))

                # Try to get enriched ingredients first, fallback to basic ingredients
                ingredients = []
                if 'detailed_ingredients' in recipe and recipe.get('detailed_ingredients'):
                    ingredients = parse_list_field(recipe.get('detailed_ingredients', ''), ',')
                elif 'enriched_ingredients' in recipe and recipe.get('enriched_ingredients'):
                    ingredients = parse_list_field(recipe.get('enriched_ingredients', ''), ',')
                else:
                    ingredients = parse_list_field(recipe.get('ingredients', ''), ',')

                instructions = parse_list_field(recipe.get('instructions', recipe.get('steps', '')), '.')
                dietary_tags = parse_list_field(recipe.get('dietary_tags', ''), ',')

                recipe_dict = {
                    'id': recipe_id,
                    'name': str(recipe.get('name', '')),
                    'description': str(recipe.get('description', '')),
                    'cookTime': int(recipe.get('minutes', 0)),
                    'difficulty': str(recipe.get('difficulty', 'medium')),
                    'ingredients': ingredients,
                    'instructions': instructions,
                    'cuisine': str(recipe.get('cuisine', '')),
                    'dietaryTags': dietary_tags,
                    'complexityScore': float(recipe.get('complexity_score', 0)),
                    'imageUrl': str(recipe.get('image_url', ''))
                }
                recipes.append(recipe_dict)
            except Exception as recipe_error:
                continue

        has_more = end_idx < total

        return jsonify({
            'recipes': recipes,
            'total': total,
            'page': page,
            'limit': limit,
            'hasMore': has_more
        })

    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/recipes/<recipe_id>', methods=['GET'])
def get_recipe_by_id(recipe_id):
    """Get a specific recipe by ID."""
    if not recipe_recommender:
        return jsonify({'error': 'Recipe recommendation service unavailable'}), 500

    try:
        # Find recipe in the model data
        recipe_data = recipe_recommender.data

        # Try multiple approaches to find the recipe
        recipe_row = None

        # Method 1: Try food_recipe_id column
        if 'food_recipe_id' in recipe_data.columns:
            try:
                recipe_row = recipe_data[recipe_data['food_recipe_id'] == int(recipe_id)]
                if not recipe_row.empty:
                    pass
            except (ValueError, TypeError):
                pass

        # Method 2: Try id column
        if (recipe_row is None or recipe_row.empty) and 'id' in recipe_data.columns:
            try:
                recipe_row = recipe_data[recipe_data['id'] == int(recipe_id)]
            except (ValueError, TypeError):
                pass

        # Method 3: Try recipe_id column
        if (recipe_row is None or recipe_row.empty) and 'recipe_id' in recipe_data.columns:
            try:
                recipe_row = recipe_data[recipe_data['recipe_id'] == recipe_id]
            except (ValueError, TypeError):
                pass

        # Method 4: Try index lookup
        if recipe_row is None or recipe_row.empty:
            try:
                recipe_row = recipe_data.loc[[int(recipe_id)]]
            except (ValueError, KeyError, TypeError):
                pass

        if recipe_row is None or recipe_row.empty:
            return jsonify({'error': 'Recipe not found'}), 404

        recipe = recipe_row.iloc[0]

        # Parse data safely using the shared function
        recipe_id = str(recipe.get('food_recipe_id', recipe.get('id', recipe.name)))

        # Try to get enriched ingredients first, fallback to basic ingredients
        ingredients = []
        if 'detailed_ingredients' in recipe and recipe.get('detailed_ingredients'):
            ingredients = parse_list_field(recipe.get('detailed_ingredients', ''), ',')
        elif 'enriched_ingredients' in recipe and recipe.get('enriched_ingredients'):
            ingredients = parse_list_field(recipe.get('enriched_ingredients', ''), ',')
        else:
            ingredients = parse_list_field(recipe.get('ingredients', ''), ',')

        instructions = parse_list_field(recipe.get('instructions', recipe.get('steps', '')), '.')
        dietary_tags = parse_list_field(recipe.get('dietary_tags', ''), ',')

        recipe_dict = {
            'id': recipe_id,
            'name': str(recipe.get('name', '')),
            'description': str(recipe.get('description', '')),
            'cookTime': int(recipe.get('minutes', 0)),
            'difficulty': str(recipe.get('difficulty', 'medium')),
            'ingredients': ingredients,
            'instructions': instructions,
            'cuisine': str(recipe.get('cuisine', '')),
            'dietaryTags': dietary_tags,
            'complexityScore': float(recipe.get('complexity_score', 0)),
            'imageUrl': str(recipe.get('image_url', ''))
        }

        return jsonify({'recipe': recipe_dict})

    except Exception as e:
        return jsonify({'error': f'Failed to get recipe: {str(e)}'}), 500

@app.route('/api/recipes/<recipe_id>/enriched-ingredients', methods=['GET'])
def get_enriched_ingredients(recipe_id):
    """Get enriched ingredient data for a recipe from the model's dataset."""
    if not recipe_recommender:
        return jsonify({'error': 'Recipe recommendation service unavailable'}), 500

    try:
        import re

        # Find recipe in the model data
        recipe_data = recipe_recommender.data

        # Try multiple approaches to find the recipe
        recipe_row = None

        # Method 1: Try food_recipe_id column
        if 'food_recipe_id' in recipe_data.columns:
            try:
                recipe_row = recipe_data[recipe_data['food_recipe_id'] == int(recipe_id)]
            except (ValueError, TypeError):
                pass

        # Method 2: Try id column
        if (recipe_row is None or recipe_row.empty) and 'id' in recipe_data.columns:
            try:
                recipe_row = recipe_data[recipe_data['id'] == int(recipe_id)]
            except (ValueError, TypeError):
                pass

        # Method 3: Try string comparison for food_recipe_id
        if (recipe_row is None or recipe_row.empty) and 'food_recipe_id' in recipe_data.columns:
            try:
                recipe_row = recipe_data[recipe_data['food_recipe_id'].astype(str) == str(recipe_id)]
            except Exception:
                pass

        # Method 4: Try index lookup
        if recipe_row is None or recipe_row.empty:
            try:
                recipe_row = recipe_data.loc[[int(recipe_id)]]
            except (ValueError, KeyError, TypeError):
                pass

        if recipe_row is None or recipe_row.empty:
            return jsonify({'error': 'Recipe not found in model data'}), 404

        recipe = recipe_row.iloc[0]

        # Try to get enriched ingredients first, fallback to basic ingredients
        if 'detailed_ingredients' in recipe and recipe.get('detailed_ingredients'):
            raw_ingredients = recipe.get('detailed_ingredients', '')
        elif 'enriched_ingredients' in recipe and recipe.get('enriched_ingredients'):
            raw_ingredients = recipe.get('enriched_ingredients', '')
        else:
            raw_ingredients = recipe.get('ingredients', '')

        basic_ingredients = parse_list_field(raw_ingredients, ',')

        # Use the ingredients we found
        detailed_ingredients = basic_ingredients

        # Parse detailed ingredients to extract quantities
        def parse_detailed_ingredient(ingredient_str):
            """Parse detailed ingredient string to extract quantity, unit, and name."""
            ingredient_str = ingredient_str.strip()

            # Enhanced regex to match more patterns including fractions and decimals
            patterns = [
                r'^(\d+(?:\s+\d+/\d+)?)\s+(\w+)\s+(.+)$',  # "1 1/2 cups flour"
                r'^(\d+/\d+)\s+(\w+)\s+(.+)$',              # "1/2 cup flour"
                r'^(\d+(?:\.\d+)?)\s+(\w+)\s+(.+)$',        # "1.5 cups flour"
                r'^(\d+)\s+(.+)$',                          # "2 eggs"
            ]

            for pattern in patterns:
                match = re.match(pattern, ingredient_str)
                if match:
                    if len(match.groups()) == 3:
                        quantity_str, unit, name = match.groups()
                    else:  # "2 eggs" pattern
                        quantity_str, name = match.groups()
                        unit = ''

                    # Parse quantity (handle fractions and mixed numbers)
                    if ' ' in quantity_str and '/' in quantity_str:
                        # Mixed number like "1 1/2"
                        whole, frac = quantity_str.split(' ', 1)
                        whole_num = float(whole)
                        num, den = frac.split('/')
                        quantity = whole_num + (float(num) / float(den))
                    elif '/' in quantity_str:
                        # Simple fraction like "1/2"
                        num, den = quantity_str.split('/')
                        quantity = float(num) / float(den)
                    else:
                        quantity = float(quantity_str)

                    # Extract preparation instructions (text in parentheses)
                    prep_match = re.search(r'\(([^)]+)\)', name)
                    preparation = prep_match.group(1) if prep_match else None
                    clean_name = re.sub(r'\s*\([^)]+\)', '', name).strip()

                    return {
                        'original': ingredient_str,
                        'quantity': quantity,
                        'unit': unit or '',
                        'name': clean_name,
                        'preparation': preparation
                    }

            # If no match, treat as name-only ingredient with quantity 1
            return {
                'original': ingredient_str,
                'quantity': 1,
                'unit': '',
                'name': ingredient_str,
                'preparation': None
            }

        # Parse all detailed ingredients
        parsed_ingredients = [parse_detailed_ingredient(ing) for ing in detailed_ingredients]

        return jsonify({
            'recipeId': recipe_id,
            'originalIngredients': basic_ingredients,
            'detailedIngredients': detailed_ingredients,
            'parsedIngredients': parsed_ingredients
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get enriched ingredients: {str(e)}'}), 500

# Saved recipes endpoints
@app.route('/api/saved-recipes', methods=['GET'])
@login_required
def get_saved_recipes():
    """Get all saved recipe IDs for the current user."""
    try:
        # Get saved recipe IDs for current user
        saved_recipe_entries = SavedRecipe.query.filter_by(user_id=current_user.user_id).all()
        saved_recipe_ids = [entry.recipe_id for entry in saved_recipe_entries]

        app_logger.debug(
            "[saved] user=%s count=%s ids=%s",
            current_user.user_id,
            len(saved_recipe_ids),
            saved_recipe_ids,
        )

        # Return just the IDs - frontend can fetch full recipe details via individual recipe endpoint
        # This avoids complex ID format mismatches and lets the frontend handle caching
        return jsonify({
            'recipes': [{'id': recipe_id} for recipe_id in saved_recipe_ids]
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get saved recipes: {str(e)}'}), 500

@app.route('/api/saved-recipes', methods=['POST'])
@login_required
def save_recipe():
    """Save a recipe for the current user."""
    data = request.get_json()
    if not data or 'recipe_id' not in data:
        return jsonify({'error': 'recipe_id is required'}), 400

    recipe_id = data['recipe_id']
    app_logger.debug("[save] attempting recipe_id=%s user=%s", recipe_id, current_user.user_id)

    try:
        # Verify the recipe exists in our model data
        if recipe_recommender:
            recipe_data = recipe_recommender.data
            recipe_found = False
            app_logger.debug("[save] model_size=%s", len(recipe_data))

            # Try to find the recipe using the same logic as the individual recipe endpoint
            if 'food_recipe_id' in recipe_data.columns:
                try:
                    recipe_row = recipe_data[recipe_data['food_recipe_id'] == int(recipe_id)]
                    if not recipe_row.empty:
                        recipe_found = True
                        app_logger.debug("[save] found via food_recipe_id")
                except (ValueError, TypeError) as e:
                    app_logger.debug("[save] food_recipe_id search failed | error=%s", e)

            if not recipe_found and 'id' in recipe_data.columns:
                try:
                    recipe_row = recipe_data[recipe_data['id'] == int(recipe_id)]
                    if not recipe_row.empty:
                        recipe_found = True
                        app_logger.debug("[save] found via id")
                except (ValueError, TypeError) as e:
                    app_logger.debug("[save] id search failed | error=%s", e)

            # Try string-based searches for non-numeric IDs
            if not recipe_found and 'recipe_id' in recipe_data.columns:
                try:
                    recipe_row = recipe_data[recipe_data['recipe_id'].astype(str) == str(recipe_id)]
                    if not recipe_row.empty:
                        recipe_found = True
                        app_logger.debug("[save] found via recipe_id string match")
                except Exception as e:
                    app_logger.debug("[save] recipe_id string search failed | error=%s", e)

            # Try index lookups (both numeric and string)
            if not recipe_found:
                try:
                    recipe_row = recipe_data.loc[[int(recipe_id)]]
                    if not recipe_row.empty:
                        recipe_found = True
                        app_logger.debug("[save] found via integer index")
                except (ValueError, KeyError, TypeError) as e:
                    app_logger.debug("[save] integer index lookup failed | error=%s", e)

            if not recipe_found:
                try:
                    recipe_row = recipe_data[recipe_data.index.astype(str) == str(recipe_id)]
                    if not recipe_row.empty:
                        recipe_found = True
                        app_logger.debug("[save] found via string index match")
                except Exception as e:
                    app_logger.debug("[save] string index lookup failed | error=%s", e)

            if not recipe_found:
                app_logger.warning("[save] recipe not found in model | recipe_id=%s", recipe_id)
                return jsonify({'error': 'Recipe not found in database'}), 400

        # Check if already saved
        app_logger.debug("[save] checking existing | user=%s recipe_id=%s", current_user.user_id, recipe_id)
        existing = SavedRecipe.query.filter_by(
            user_id=current_user.user_id,
            recipe_id=recipe_id
        ).first()

        if existing:
            app_logger.info("[save] already saved | user=%s recipe_id=%s", current_user.user_id, recipe_id)
            return jsonify({'error': 'Recipe already saved'}), 400

        # Save the recipe
        app_logger.info("[save] saving | user=%s recipe_id=%s", current_user.user_id, recipe_id)
        saved_recipe = SavedRecipe(
            user_id=current_user.user_id,
            recipe_id=recipe_id
        )
        db.session.add(saved_recipe)
        db.session.commit()
        app_logger.info("[save] success | user=%s recipe_id=%s", current_user.user_id, recipe_id)

        return jsonify({'message': 'Recipe saved successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save recipe: {str(e)}'}), 500

@app.route('/api/saved-recipes/<recipe_id>', methods=['DELETE'])
@login_required
def remove_saved_recipe(recipe_id):
    """Remove a saved recipe for the current user."""
    app_logger.debug("[delete] attempting | user=%s recipe_id=%s", current_user.user_id, recipe_id)
    try:
        saved_recipe = SavedRecipe.query.filter_by(
            user_id=current_user.user_id,
            recipe_id=recipe_id
        ).first()

        if not saved_recipe:
            app_logger.info("[delete] not found | user=%s recipe_id=%s", current_user.user_id, recipe_id)
            # Optionally include current saved IDs for debugging
            all_saved = SavedRecipe.query.filter_by(user_id=current_user.user_id).all()
            saved_ids = [r.recipe_id for r in all_saved]
            app_logger.debug("[delete] user saved ids | user=%s ids=%s", current_user.user_id, saved_ids)
            return jsonify({'error': 'Recipe not found in saved recipes'}), 404

        app_logger.info("[delete] deleting | user=%s recipe_id=%s", current_user.user_id, recipe_id)
        db.session.delete(saved_recipe)
        db.session.commit()
        app_logger.info("[delete] success | user=%s recipe_id=%s", current_user.user_id, recipe_id)

        return jsonify({'message': 'Recipe removed from saved recipes'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove saved recipe: {str(e)}'}), 500

@app.route("/")
@login_required
def home():
    '''Home route that returns a welcome message.'''
    return render_template("index.html")

# Serve SPA login route so Flask-Login redirects work in production
@app.route('/login')
def login_page():
    return render_template("index.html")

# Catch-all route for SPA - handles all frontend routes like /registration, /dashboard, etc.
@app.route('/<path:path>')
def spa_routes(path):
    # Only serve SPA for non-API routes
    if not path.startswith('api/'):
        return render_template("index.html")
    # Let Flask handle 404 for unknown API routes
    return jsonify({'error': 'Not found'}), 404

# Serve Vite-built assets at /assets/* (copied to static/assets in container)
@app.route('/assets/<path:filename>')
def vite_assets(filename):
    assets_dir = os.path.join(app.root_path, 'static', 'assets')
    return send_from_directory(assets_dir, filename)

# Return JSON for API 500 errors so the frontend doesn't try to parse HTML
@app.errorhandler(500)
def api_json_500(e):
    p = request.path or ''
    if p.startswith('/api'):
        return jsonify({'error': 'Internal server error'}), 500
    return e

# SPA fallback: serve index.html for any non-API, non-static path
@app.errorhandler(404)
def spa_fallback(e):
    path = request.path.lstrip('/')
    # Let API and static 404s pass through
    if path.startswith('api') or path.startswith('assets') or path.startswith('static'):
        return e
    # Serve SPA index for client routes like /registration, /recommendations, etc.
    return render_template('index.html')

# Ensure database tables exist at import time (safe and idempotent for SQLite/dev)
try:
    with app.app_context():
        db.create_all()
except Exception:
    pass

# Entry point: ensure all routes are registered before running the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # Do not enable debug in production
    app.run(debug=(ENVIRONMENT != 'production'))
