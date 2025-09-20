import os
import sys
from pathlib import Path
import pytest


# Ensure the Flask app module is importable and has a DB URI during import
ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / 'food-recipe-recommender' / 'app'
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# Provide sane defaults for app import time (override blank values too)
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
os.environ.setdefault("ENV", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")

from app import app as flask_app, db  # type: ignore


@pytest.fixture
def client():
    # Configure an in-memory SQLite DB for isolated tests
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret",
        "ENV": "test",
    })

    with flask_app.app_context():
        db.create_all()

    with flask_app.test_client() as client:
        yield client

    # Cleanup
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()
