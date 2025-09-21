"""Configuration settings for the Flask application."""

from __future__ import annotations

from pathlib import Path
import os

class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")  # Load from env for production
    BASE_DIR = Path(__file__).resolve().parents[1]
    MODELS_DIR = BASE_DIR / "models"
    MODEL_FILENAME = "recipe_recommender_model.joblib"
    SCALER_FILENAME = "scaler.joblib"
    RECOMMENDATION_LIMIT = 5
    SEARCH_LIMIT = 10
