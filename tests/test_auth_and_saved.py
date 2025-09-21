import json


def register(client, email="user@example.com", password="password123", full_name="Test User"):
    return client.post(
        "/api/register",
        data=json.dumps(
            {
                "email": email,
                "password": password,
                "full_name": full_name,
                "newsletter_signup": False,
            }
        ),
        content_type="application/json",
    )


def test_register_and_auth_me(client):
    res = register(client)
    assert res.status_code == 200
    body = res.get_json()
    assert body.get("success") is True

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    data = me.get_json()
    assert data.get("authenticated") is True
    assert data.get("user", {}).get("email") == "user@example.com"


def test_save_list_delete_recipe_flow(client, monkeypatch):
    # Ensure a recipe with id=123 exists in the model
    import pandas as pd

    class Rec:
        def __init__(self):
            self.data = pd.DataFrame(
                [
                    {
                        "id": 123,
                        "name": "Exists",
                        "minutes": 1,
                        "difficulty": "easy",
                        "ingredients": "[]",
                        "steps": "",
                    }
                ]
            )

    import app as app_module  # type: ignore

    app_module.recipe_recommender = Rec()
    # Must be authenticated
    assert register(client).status_code == 200

    # Initially empty
    res = client.get("/api/saved-recipes")
    assert res.status_code == 200
    assert res.get_json().get("recipes") == []

    # Save a recipe
    res = client.post(
        "/api/saved-recipes",
        data=json.dumps({"recipe_id": "123"}),
        content_type="application/json",
    )
    assert res.status_code == 200

    # Duplicate save rejected
    res_dup = client.post(
        "/api/saved-recipes",
        data=json.dumps({"recipe_id": "123"}),
        content_type="application/json",
    )
    assert res_dup.status_code == 400

    # List contains the saved id
    res = client.get("/api/saved-recipes")
    assert res.status_code == 200
    saved = res.get_json().get("recipes")
    assert saved == [{"id": "123"}]

    # Delete it
    res = client.delete("/api/saved-recipes/123")
    assert res.status_code == 200

    # Now empty again
    res = client.get("/api/saved-recipes")
    assert res.status_code == 200
    assert res.get_json().get("recipes") == []


def test_save_recipe_requires_recipe_id(client):
    assert register(client).status_code == 200
    res = client.post(
        "/api/saved-recipes",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert res.status_code == 400
