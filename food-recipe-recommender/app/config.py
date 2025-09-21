"""Configuration settings for the Flask application."""

from __future__ import annotations

from pathlib import Path


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = "dev-secret-key"  # Replace for production
    BASE_DIR = Path(__file__).resolve().parents[1]
    MODELS_DIR = BASE_DIR / "models"
    MODEL_FILENAME = "recipe_recommender_model.joblib"
    SCALER_FILENAME = "scaler.joblib"
    RECOMMENDATION_LIMIT = 5
    SEARCH_LIMIT = 10
