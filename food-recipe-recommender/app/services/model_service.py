"""Utilities for loading the trained recommender model and associated assets."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
from flask import current_app


class ModelLoadError(RuntimeError):
    """Raised when the recommender model cannot be loaded."""


def _models_dir() -> Path:
    models_dir = Path(current_app.config["MODELS_DIR"])
    if not models_dir.exists():
        raise ModelLoadError(
            f"Models directory not found at {models_dir}. Have you trained the model?"
        )
    return models_dir


def _model_path() -> Path:
    return _models_dir() / current_app.config["MODEL_FILENAME"]


@lru_cache(maxsize=1)
def load_recommender() -> Any:
    """Load and cache the trained RecipeRecommender model."""
    model_path = _model_path()
    if not model_path.exists():
        raise ModelLoadError(
            f"Model file not found at {model_path}. Please train or provide the model."
        )

    try:
        return joblib.load(model_path)
    except Exception as exc:  # noqa: BLE001
        raise ModelLoadError(
            f"Failed to load model from {model_path}: {exc}"
        ) from exc


def load_scaler() -> Any:
    """Load the fitted scaler used for feature normalization."""
    scaler_path = _models_dir() / current_app.config["SCALER_FILENAME"]
    if not scaler_path.exists():
        raise ModelLoadError(
            f"Scaler file not found at {scaler_path}."
        )

    try:
        return joblib.load(scaler_path)
    except Exception as exc:  # noqa: BLE001
        raise ModelLoadError(
            f"Failed to load scaler from {scaler_path}: {exc}"
        ) from exc
