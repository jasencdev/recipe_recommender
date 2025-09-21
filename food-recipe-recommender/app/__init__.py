import os
import logging
import joblib
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.engine.url import make_url

db = SQLAlchemy()
login_manager = LoginManager()


def create_app() -> Flask:
    app = Flask(__name__, static_folder='static', template_folder='templates')
    CORS(app, supports_credentials=True)

    # Config and env
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
    app.config['ENVIRONMENT'] = os.getenv('ENV', 'development')
    app.config['ADMIN_TOKEN'] = os.getenv('ADMIN_TOKEN')
    app.config['RESEND_API_KEY'] = os.getenv('RESEND_API_KEY')
    app.config['EMAIL_FROM'] = os.getenv('EMAIL_FROM', 'Recipe Recommender <no-reply@example.com>')
    app.config['FRONTEND_BASE_URL'] = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')
    app.config['RATE_LIMIT_PER_IP_PER_HOUR'] = int(os.getenv('RATE_LIMIT_PER_IP_PER_HOUR', '5').strip('"'))
    app.config['RATE_LIMIT_PER_EMAIL_PER_HOUR'] = int(os.getenv('RATE_LIMIT_PER_EMAIL_PER_HOUR', '3').strip('"'))

    # Logging
    _log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(level=getattr(logging, _log_level, logging.INFO), format='%(asctime)s %(levelname)s %(name)s %(message)s')

    # Database URL with fallback
    _db_url_env = (os.getenv('DATABASE_URL') or '').strip()
    if not _db_url_env:
        _db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
        os.makedirs(os.path.dirname(_db_path), exist_ok=True)
        _db_url = f'sqlite:///{_db_path}'
    else:
        try:
            make_url(_db_url_env)
            _db_url = _db_url_env
        except Exception:
            _db_path = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
            os.makedirs(os.path.dirname(_db_path), exist_ok=True)
            _db_url = f'sqlite:///{_db_path}'
    app.config['SQLALCHEMY_DATABASE_URI'] = _db_url

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = '/login'

    # Load recommender model if available
    try:
        base_dir = os.path.dirname(__file__)
        model_path = os.path.abspath(os.path.join(base_dir, '..', 'models', 'recipe_recommender_model.joblib'))
        app.config['RECOMMENDER'] = joblib.load(model_path)
    except Exception:
        app.config['RECOMMENDER'] = None

    # Models and user loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception:
            return None

    # Blueprints
    from .blueprints.misc import misc_bp
    from .blueprints.auth import auth_bp
    from .blueprints.saved import saved_bp
    from .blueprints.recipes import recipes_bp
    app.register_blueprint(misc_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(saved_bp)
    app.register_blueprint(recipes_bp)

    # Idempotent DB init for dev/SQLite
    try:
        with app.app_context():
            db.create_all()
    except Exception:
        pass

    # Static assets and SPA handling
    @app.route('/assets/<path:filename>')
    def vite_assets(filename):
        assets_dir = os.path.join(app.root_path, 'static', 'assets')
        return send_from_directory(assets_dir, filename)

    @app.get('/')
    def home():
        return render_template('index.html')

    @app.get('/login')
    def login_page():
        return render_template('index.html')

    @app.errorhandler(500)
    def api_json_500(e):
        p = request.path or ''
        if p.startswith('/api'):
            return jsonify({'error': 'Internal server error'}), 500
        return e

    @app.errorhandler(404)
    def spa_fallback(e):
        path = request.path.lstrip('/')
        if path.startswith('api') or path.startswith('assets') or path.startswith('static'):
            return e
        return render_template('index.html')

    return app

