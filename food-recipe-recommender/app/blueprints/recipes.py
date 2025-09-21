import logging
from typing import Tuple

from flask import Blueprint, Response, jsonify, request

from ..services.recipes_utils import extract_ingredients_fields, find_row_by_id, resolve_recommender
from ..utils import parse_list_field

recipes_bp = Blueprint("recipes", __name__)
_logger = logging.getLogger(__name__)


def _resolve_recommender():
    return resolve_recommender()


@recipes_bp.get("/api/search")
def search() -> Tuple[Response, int]:
    recommender = _resolve_recommender()
    if not recommender:
        return jsonify({"error": "Recipe recommendation service unavailable"}), 500

    query = request.args.get("query", "").strip()
    complexity_score = request.args.get("complexity_score", type=float)
    number_of_ingredients = request.args.get("number_of_ingredients", type=int)
    cook_time = request.args.get("cook_time", type=int)
    cuisine = request.args.get("cuisine", "").strip()
    dietary_restrictions = request.args.get("dietary_restrictions", "").strip()
    page = max(1, request.args.get("page", 1, type=int))
    limit = max(1, min(100, request.args.get("limit", 20, type=int)))  # Limit between 1-100

    # Validate numeric inputs
    if complexity_score is not None and (complexity_score < 0 or complexity_score > 100):
        return jsonify({"error": "Complexity score must be between 0 and 100"}), 400
    if number_of_ingredients is not None and number_of_ingredients < 1:
        return jsonify({"error": "Number of ingredients must be at least 1"}), 400
    if cook_time is not None and cook_time < 1:
        return jsonify({"error": "Cook time must be at least 1 minute"}), 400

    try:
        if (
            complexity_score is not None
            or cook_time is not None
            or number_of_ingredients is not None
        ):
            desired_complexity = complexity_score if complexity_score is not None else 25
            desired_time = cook_time if cook_time is not None else 30
            desired_ingredients = number_of_ingredients if number_of_ingredients is not None else 10
            all_recipes = recommender.recommend_recipes(
                desired_time, desired_complexity, desired_ingredients, n_recommendations=1000
            )
        elif query:
            all_recipes = recommender.search_recipes(query, n_results=1000)
        else:
            all_recipes = recommender.data.copy()

        if cuisine and "cuisine" in all_recipes.columns:
            all_recipes = all_recipes[
                all_recipes["cuisine"].str.contains(cuisine, case=False, na=False)
            ]
        if dietary_restrictions and "dietary_tags" in all_recipes.columns:
            for d in [x.strip() for x in dietary_restrictions.split(",")]:
                all_recipes = all_recipes[
                    all_recipes["dietary_tags"].str.contains(d, case=False, na=False)
                ]

        total = len(all_recipes)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated = all_recipes.iloc[start_idx:end_idx]

        recipes = []
        for _, r in paginated.iterrows():
            try:
                rid = str(r.get("food_recipe_id", r.get("id", r.name)))
                ingredients, instructions, dietary_tags = extract_ingredients_fields(r)
                recipes.append(
                    {
                        "id": rid,
                        "name": str(r.get("name", "")),
                        "description": str(r.get("description", "")),
                        "cookTime": int(r.get("minutes", 0)),
                        "difficulty": str(r.get("difficulty", "medium")),
                        "ingredients": ingredients,
                        "instructions": instructions,
                        "cuisine": str(r.get("cuisine", "")),
                        "dietaryTags": dietary_tags,
                        "complexityScore": float(r.get("complexity_score", 0)),
                        "imageUrl": str(r.get("image_url", "")),
                    }
                )
            except Exception as e:
                _logger.debug("[recipes.search] skipping row due to error: %s", e)
                continue

        return jsonify(
            {
                "recipes": recipes,
                "total": total,
                "page": page,
                "limit": limit,
                "hasMore": end_idx < total,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Search failed: {e}"}), 500


@recipes_bp.get("/api/recipes/<recipe_id>")
def get_recipe(recipe_id: str) -> Tuple[Response, int]:
    recommender = _resolve_recommender()
    if not recommender:
        return jsonify({"error": "Recipe recommendation service unavailable"}), 500
    try:
        data = recommender.data
        row = find_row_by_id(data, recipe_id)
        if row is None or row.empty:
            return jsonify({"error": "Recipe not found"}), 404
        r = row.iloc[0]
        rid = str(r.get("food_recipe_id", r.get("id", r.name)))
        ingredients, instructions, dietary_tags = extract_ingredients_fields(r)
        return jsonify(
            {
                "recipe": {
                    "id": rid,
                    "name": str(r.get("name", "")),
                    "description": str(r.get("description", "")),
                    "cookTime": int(r.get("minutes", 0)),
                    "difficulty": str(r.get("difficulty", "medium")),
                    "ingredients": ingredients,
                    "instructions": instructions,
                    "cuisine": str(r.get("cuisine", "")),
                    "dietaryTags": dietary_tags,
                    "complexityScore": float(r.get("complexity_score", 0)),
                    "imageUrl": str(r.get("image_url", "")),
                }
            }
        )
    except Exception as e:
        return jsonify({"error": f"Failed to get recipe: {e}"}), 500


@recipes_bp.get("/api/recipes/<recipe_id>/enriched-ingredients")
def enriched_ingredients(recipe_id: str) -> Tuple[Response, int]:
    recommender = _resolve_recommender()
    if not recommender:
        return jsonify({"error": "Recipe recommendation service unavailable"}), 500
    try:
        data = recommender.data
        row = find_row_by_id(data, recipe_id)
        if row is None or row.empty:
            return jsonify({"error": "Recipe not found in model data"}), 404
        rec = row.iloc[0]
        if "detailed_ingredients" in rec and rec.get("detailed_ingredients"):
            raw_ingredients = rec.get("detailed_ingredients", "")
        elif "enriched_ingredients" in rec and rec.get("enriched_ingredients"):
            raw_ingredients = rec.get("enriched_ingredients", "")
        else:
            raw_ingredients = rec.get("ingredients", "")
        basic_ingredients = parse_list_field(raw_ingredients, ",")

        import re

        def parse_detailed_ingredient(ingredient_str):
            ingredient_str = ingredient_str.strip()
            patterns = [
                r"^(\d+(?:\s+\d+/\d+)?)\s+(\w+)\s+(.+)$",
                r"^(\d+/\d+)\s+(\w+)\s+(.+)$",
                r"^(\d+(?:\.\d+)?)\s+(\w+)\s+(.+)$",
                r"^(\d+)\s+(.+)$",
            ]
            for pattern in patterns:
                match = re.match(pattern, ingredient_str)
                if match:
                    if len(match.groups()) == 3:
                        quantity_str, unit, name = match.groups()
                    else:
                        quantity_str, name = match.groups()
                        unit = ""
                    if " " in quantity_str and "/" in quantity_str:
                        whole, frac = quantity_str.split(" ", 1)
                        whole_num = float(whole)
                        num, den = frac.split("/")
                        quantity = whole_num + (float(num) / float(den))
                    elif "/" in quantity_str:
                        num, den = quantity_str.split("/")
                        quantity = float(num) / float(den)
                    else:
                        quantity = float(quantity_str)
                    prep_match = re.search(r"\(([^)]+)\)", name)
                    preparation = prep_match.group(1) if prep_match else None
                    clean_name = re.sub(r"\s*\([^)]+\)", "", name).strip()
                    return {
                        "original": ingredient_str,
                        "quantity": quantity,
                        "unit": unit or "",
                        "name": clean_name,
                        "preparation": preparation,
                    }
            return {
                "original": ingredient_str,
                "quantity": 1,
                "unit": "",
                "name": ingredient_str,
                "preparation": None,
            }

        parsed_ingredients = [parse_detailed_ingredient(ing) for ing in basic_ingredients]
        detailed_text = [p.get("original") or p.get("name") for p in parsed_ingredients]
        return jsonify(
            {
                "recipeId": recipe_id,
                "originalIngredients": basic_ingredients,
                "detailedIngredients": detailed_text,
                "parsedIngredients": parsed_ingredients,
            }
        )
    except Exception as e:
        return jsonify({"error": f"Failed to get enriched ingredients: {e}"}), 500
