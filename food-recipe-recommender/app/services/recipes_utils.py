from __future__ import annotations

import logging
from typing import Any

from flask import current_app

from ..utils import parse_list_field


def resolve_recommender():
    try:
        import app as app_module  # type: ignore
        if hasattr(app_module, "recipe_recommender"):
            return app_module.recipe_recommender
    except Exception as e:
        logging.getLogger(__name__).debug("[resolve_recommender] legacy shim not available: %s", e)
    return current_app.config.get("RECOMMENDER")


def find_row_by_id(df, recipe_id: str):
    """Locate a recipe row in the recommender dataframe by trying common id fields.
    Returns a dataframe slice (possibly empty).
    """
    row = None
    try:
        if "food_recipe_id" in df.columns:
            try:
                rid_int = int(recipe_id)
                row = df[df["food_recipe_id"] == rid_int]
            except Exception:
                row = df[df["food_recipe_id"].astype(str) == str(recipe_id)]
    except Exception as e:
        logging.getLogger(__name__).debug("[find_row_by_id] error checking food_recipe_id column: %s", e)
    if (row is None or getattr(row, "empty", True)) and "id" in df.columns:
        try:
            rid_int = int(recipe_id)
            row = df[df["id"] == rid_int]
        except Exception:
            row = df[df["id"].astype(str) == str(recipe_id)]
    if (row is None or getattr(row, "empty", True)) and "recipe_id" in df.columns:
        try:
            row = df[df["recipe_id"] == recipe_id]
        except Exception as e:
            logging.getLogger(__name__).debug("[find_row_by_id] error using recipe_id string match: %s", e)
    # Try index lookup by string key before attempting int
    if row is None or getattr(row, "empty", True):
        try:
            row = df.loc[[recipe_id]]
        except Exception as e:
            logging.getLogger(__name__).debug("[find_row_by_id] string index lookup failed: %s", e)
    if row is None or getattr(row, "empty", True):
        try:
            row = df.loc[[int(recipe_id)]]
        except Exception as e:
            logging.getLogger(__name__).debug("[find_row_by_id] numeric index lookup failed: %s", e)
    return row


def extract_ingredients_fields(rec: Any) -> tuple[list[str], list[str], list[str]]:
    """Extract ingredients, instructions, dietary_tags in a consistent way.
    Returns (ingredients, instructions, dietary_tags).
    """
    if "detailed_ingredients" in rec and rec.get("detailed_ingredients"):
        ingredients = parse_list_field(rec.get("detailed_ingredients", ""), ",")
    elif "enriched_ingredients" in rec and rec.get("enriched_ingredients"):
        ingredients = parse_list_field(rec.get("enriched_ingredients", ""), ",")
    else:
        ingredients = parse_list_field(rec.get("ingredients", ""), ",")
    instructions = parse_list_field(rec.get("instructions", rec.get("steps", "")), ".")
    dietary_tags = parse_list_field(rec.get("dietary_tags", ""), ",")
    return ingredients, instructions, dietary_tags
