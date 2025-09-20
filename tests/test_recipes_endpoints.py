import json
from datetime import datetime, timedelta

import pandas as pd
import pytest


def mount_fake_recommender(monkeypatch):
    # Build a dataframe with various id patterns and ingredient fields
    df = pd.DataFrame([
        {
            "food_recipe_id": 10,
            "id": 1001,
            "recipe_id": "abc123",
            "name": "Spaghetti",
            "minutes": 20,
            "difficulty": "easy",
            "detailed_ingredients": json.dumps(["1 1/2 cups flour", "2 eggs (beaten)"]),
            "steps": "Boil. Mix.",
            "cuisine": "italian",
            "dietary_tags": "vegan,healthy",
            "complexity_score": 5.0,
            "image_url": "",
        },
        {
            "food_recipe_id": 11,
            "id": 2,
            "name": "Curry",
            "minutes": 40,
            "difficulty": "medium",
            "enriched_ingredients": json.dumps(["1/2 cup milk", "3 tbsp oil"]),
            "steps": "Simmer. Serve.",
            "cuisine": "indian",
            "dietary_tags": "vegan",
            "complexity_score": 20.0,
            "image_url": "",
        },
    ])

    class FakeRecommender:
        def __init__(self, data):
            self.data = data

        def recommend_recipes(self, desired_time, desired_complexity, desired_ingredients, n_recommendations):
            return self.data

        def search_recipes(self, query, n_results):
            return self.data[self.data["name"].str.contains(query, case=False, na=False)] if query else self.data

    import app as app_module  # type: ignore
    monkeypatch.setattr(app_module, "recipe_recommender", FakeRecommender(df), raising=False)
    return df


def register_and_login(client, email="test@example.com", password="pw", full_name="T User"):
    r = client.post(
        "/api/register",
        data=json.dumps({"email": email, "password": password, "full_name": full_name}),
        content_type="application/json",
    )
    assert r.status_code == 200


def test_search_branches_and_filters(client, monkeypatch):
    mount_fake_recommender(monkeypatch)

    # query-based search
    r = client.get("/api/search", query_string={"query": "spa", "cuisine": "ital", "dietary_restrictions": "vegan"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["total"] >= 1
    assert any("Spaghetti" in rec["name"] for rec in body["recipes"])  # matched query

    # model-based filters (complexity, time, ingredients)
    r = client.get("/api/search", query_string={"complexity_score": 5, "cook_time": 30, "number_of_ingredients": 10})
    assert r.status_code == 200


def test_recipe_by_id_variants(client, monkeypatch):
    df = mount_fake_recommender(monkeypatch)

    # food_recipe_id match
    r = client.get("/api/recipes/10")
    assert r.status_code == 200
    assert r.get_json()["recipe"]["name"] == "Spaghetti"

    # id match
    r = client.get("/api/recipes/2")
    assert r.status_code == 200
    assert r.get_json()["recipe"]["name"] == "Curry"

    # recipe_id string match
    r = client.get("/api/recipes/abc123")
    assert r.status_code == 200


def test_enriched_ingredients_parsing(client, monkeypatch):
    mount_fake_recommender(monkeypatch)
    r = client.get("/api/recipes/10/enriched-ingredients")
    assert r.status_code == 200
    data = r.get_json()
    parsed = data["parsedIngredients"]
    # Should parse quantities and units; allow flexible wording for eggs
    assert any(item["unit"] in ("cups", "cup") or item["unit"] for item in parsed)
    # Either unit or name should reflect eggs
    assert any("egg" in (str(item.get("unit", "")) + " " + str(item.get("name", ""))).lower() for item in parsed)


def test_saved_recipes_full_flow(client, monkeypatch):
    mount_fake_recommender(monkeypatch)
    register_and_login(client)

    # Initially empty
    r = client.get("/api/saved-recipes")
    assert r.status_code == 200
    assert r.get_json()["recipes"] == []

    # Missing body
    r = client.post("/api/saved-recipes", data=json.dumps({}), content_type="application/json")
    assert r.status_code == 400

    # Not found in model
    r = client.post("/api/saved-recipes", data=json.dumps({"recipe_id": "999999"}), content_type="application/json")
    assert r.status_code == 400

    # Save valid
    r = client.post("/api/saved-recipes", data=json.dumps({"recipe_id": "10"}), content_type="application/json")
    assert r.status_code == 200

    # Duplicate
    r = client.post("/api/saved-recipes", data=json.dumps({"recipe_id": "10"}), content_type="application/json")
    assert r.status_code == 400

    # List includes id
    r = client.get("/api/saved-recipes")
    ids = [x["id"] for x in r.get_json()["recipes"]]
    assert "10" in ids

    # Delete not found
    r = client.delete("/api/saved-recipes/999999")
    assert r.status_code == 404

    # Delete valid
    r = client.delete("/api/saved-recipes/10")
    assert r.status_code == 200
