def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data == {"status": "healthy"}


def test_saved_recipes_requires_auth(client):
    res = client.get("/api/saved-recipes")
    # Flask-Login may return 401 for API requests or 302 redirect to login
    assert res.status_code in (401, 302)
