"""Service functions to interact with the RecipeRecommender model."""

from __future__ import annotations

import ast
from typing import Any, Iterable

import pandas as pd


def build_recommendation_context(
    *,
    user_name: str | None = None,
    cook_time: int | None = None,
    complexity: int | None = None,
    recommendations: list[dict[str, Any]] | None = None,
    search_query: str | None = None,
    search_results: list[dict[str, Any]] | None = None,
    model_loaded: bool = False,
) -> dict[str, Any]:
    """Assemble template context for rendering the UI."""
    return {
        "user_name": user_name or "",
        "cook_time": cook_time,
        "complexity": complexity,
        "recommendations": recommendations or [],
        "search_query": search_query or "",
        "search_results": search_results or [],
        "model_loaded": model_loaded,
    }


def get_recommendations(
    model: Any,
    *,
    cook_time: int,
    complexity: int,
    limit: int,
) -> list[dict[str, Any]]:
    """Fetch recipe recommendations using the trained model."""
    results = model.recommend_recipes(
        desired_time=cook_time,
        desired_complexity=complexity,
        n_recommendations=limit,
    )
    return _serialise_results(results)


def search_recipes(
    model: Any,
    *,
    query: str,
    limit: int,
) -> list[dict[str, Any]]:
    """Search recipes using the trained model."""
    results = model.search_recipes(query, n_results=limit)
    return _serialise_results(results)


def _serialise_results(results: Any) -> list[dict[str, Any]]:
    """Convert a pandas DataFrame of recipes to template-friendly dictionaries."""
    if results is None:
        return []

    if isinstance(results, pd.DataFrame):
        records = results.to_dict(orient="records")
    elif isinstance(results, Iterable):
        records = list(results)
    else:
        raise ValueError("Unexpected results format from recommender model")

    serialised: list[dict[str, Any]] = []
    for record in records:
        ingredients = _safe_parse_list(record.get("ingredients"))
        steps = _safe_parse_list(record.get("steps"))
        serialised.append(
            {
                "name": record.get("name", "Unknown Recipe"),
                "minutes": record.get("minutes"),
                "complexity": record.get("complexity_score"),
                "ingredients": ingredients,
                "steps": steps,
            }
        )
    return serialised


def _safe_parse_list(raw_value: Any) -> list[str]:
    """Safely parse a stored list representation into a Python list."""
    if isinstance(raw_value, list):
        return [str(item) for item in raw_value]
    if not raw_value:
        return []
    if not isinstance(raw_value, str):
        return [str(raw_value)]
    try:
        parsed = ast.literal_eval(raw_value)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (ValueError, SyntaxError):
        return [raw_value]
    return [raw_value]
