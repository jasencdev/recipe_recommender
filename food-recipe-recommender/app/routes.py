"""Application routes and request handlers."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .config import Config
from .services.model_service import ModelLoadError, load_recommender
from .services.recommendation_service import (
    build_recommendation_context,
    get_recommendations,
    search_recipes,
)

bp = Blueprint("main", __name__)


def _ensure_model():
    """Attempt to load the recommender model and surface friendly errors."""
    try:
        return load_recommender()
    except ModelLoadError as exc:
        flash(str(exc), "error")
        return None


@bp.route("/", methods=["GET"])
def index():
    """Render the landing page with empty context."""
    model = _ensure_model()
    context = build_recommendation_context()
    context["model_loaded"] = model is not None
    return render_template("index.html", **context)


@bp.route("/recommend", methods=["POST"])
def recommend():
    """Handle recommendation form submissions."""
    model = _ensure_model()
    if model is None:
        return redirect(url_for("main.index"))

    user_name = request.form.get("user_name", "").strip()
    cook_time = request.form.get("cook_time", "").strip()
    complexity = request.form.get("complexity", "").strip()

    try:
        cook_time_value = int(cook_time)
        complexity_value = int(complexity)
    except ValueError:
        flash("Cook time and complexity must be numeric values.", "error")
        return redirect(url_for("main.index"))

    try:
        recommendations = get_recommendations(
            model,
            cook_time=cook_time_value,
            complexity=complexity_value,
            limit=Config.RECOMMENDATION_LIMIT,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index"))

    context = build_recommendation_context(
        user_name=user_name,
        cook_time=cook_time_value,
        complexity=complexity_value,
        recommendations=recommendations,
        model_loaded=True,
    )
    return render_template("index.html", **context)


@bp.route("/search", methods=["POST"])
def search():
    """Handle search form submissions."""
    model = _ensure_model()
    if model is None:
        return redirect(url_for("main.index"))

    query = request.form.get("search_query", "").strip()
    if not query:
        flash("Please enter a search query.", "error")
        return redirect(url_for("main.index"))

    try:
        results = search_recipes(
            model,
            query=query,
            limit=Config.SEARCH_LIMIT,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("main.index"))

    context = build_recommendation_context(
        search_query=query,
        search_results=results,
        model_loaded=True,
    )
    return render_template("index.html", **context)
