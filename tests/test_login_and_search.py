import json

import pandas as pd


def login(client, email: str, password: str):
    return client.post(
        "/api/login",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )


def test_login_logout_flow(client):
    # Register a new user
    res = client.post(
        "/api/register",
        data=json.dumps(
            {
                "email": "user@example.com",
                "password": "secret123",
                "full_name": "Tester",
            }
        ),
        content_type="application/json",
    )
    assert res.status_code == 200

    # Wrong password
    bad = login(client, "user@example.com", "wrong")
    assert bad.status_code == 401

    # Correct login
    ok = login(client, "user@example.com", "secret123")
    assert ok.status_code == 200

    # Auth check shows authenticated
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.get_json().get("authenticated") is True

    # Logout
    out = client.post("/api/logout")
    assert out.status_code == 200

    # Auth check after logout should be unauthorized
    me2 = client.get("/api/auth/me")
    assert me2.status_code == 401


def test_search_params_validation_and_filters(client, monkeypatch):
    # Build a minimal fake recommender with dataframe + methods
    df = pd.DataFrame(
        [
            {
                "id": 1,
                "name": "Pasta Primavera",
                "minutes": 25,
                "difficulty": "easy",
                "ingredients": '["pasta", "vegetables"]',
                "steps": "Boil. Mix.",
                "cuisine": "italian",
                "dietary_tags": "healthy,vegetarian",
                "complexity_score": 10.0,
                "image_url": "",
            },
            {
                "id": 2,
                "name": "Vegan Curry",
                "minutes": 40,
                "difficulty": "medium",
                "ingredients": '["tofu", "curry paste"]',
                "steps": "Simmer. Serve.",
                "cuisine": "indian",
                "dietary_tags": "healthy,vegan",
                "complexity_score": 20.0,
                "image_url": "",
            },
        ]
    )

    class FakeRecommender:
        def __init__(self, data):
            self.data = data

        def recommend_recipes(
            self, desired_time, desired_complexity, desired_ingredients, n_recommendations
        ):
            return self.data

        def search_recipes(self, query, n_results):
            return (
                self.data[self.data["name"].str.contains(query, case=False, na=False)]
                if query
                else self.data
            )

    # Patch into the app module
    import app as app_module  # type: ignore

    monkeypatch.setattr(app_module, "recipe_recommender", FakeRecommender(df), raising=False)

    # Invalid types for numeric params shouldn't crash (they become None via type casting)
    res = client.get(
        "/api/search",
        query_string={
            "complexity_score": "not-a-number",
            "number_of_ingredients": "NaN",
            "cook_time": "",
            "page": "1",
            "limit": "10",
        },
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data.get("total") == 2
    assert len(data.get("recipes")) == 2

    # Apply cuisine filter
    res2 = client.get("/api/search", query_string={"cuisine": "italian"})
    d2 = res2.get_json()
    assert res2.status_code == 200
    assert d2.get("total") == 1
    assert d2["recipes"][0]["name"].lower().startswith("pasta")

    # Apply dietary restriction filter
    res3 = client.get("/api/search", query_string={"dietary_restrictions": "vegan"})
    d3 = res3.get_json()
    assert res3.status_code == 200
    assert d3.get("total") == 1
    assert d3["recipes"][0]["name"].lower().startswith("vegan")
