"""Flask application factory for the recipe recommender web app."""

from flask import Flask

from .config import Config


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    return app


app = create_app()
