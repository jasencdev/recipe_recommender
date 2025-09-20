import json
from datetime import datetime, timedelta

import pandas as pd
import pytest


def test_parse_list_field_cases():
    from app import parse_list_field  # type: ignore

    # Non-string input returns []
    assert parse_list_field(None) == []
    assert parse_list_field(123) == []

    # JSON list
    assert parse_list_field('["a", "b"]') == ["a", "b"]

    # Invalid JSON falls through to literal/CSV parsing
    assert parse_list_field('[\'a\', \'b\']') == ["a", "b"]

    # CSV fallback strips quotes/brackets
    assert parse_list_field("['x', 'y']", ',') == ["x", "y"]
    assert parse_list_field("x,y", ',') == ["x", "y"]


def test_register_login_negative(client):
    # Register user
    r = client.post('/api/register', data=json.dumps({
        'email': 'dup@example.com',
        'password': 'pw',
        'full_name': 'Dup User',
    }), content_type='application/json')
    assert r.status_code == 200

    # Duplicate email
    r = client.post('/api/register', data=json.dumps({
        'email': 'dup@example.com',
        'password': 'pw',
        'full_name': 'Dup User',
    }), content_type='application/json')
    assert r.status_code == 400

    # Login GET
    r = client.get('/api/login')
    assert r.status_code == 401

    # Login bad/empty body
    r = client.post('/api/login', data=json.dumps({}), content_type='application/json')
    assert r.status_code == 400

    # Invalid credentials
    r = client.post('/api/login', data=json.dumps({'email': 'dup@example.com', 'password': 'wrong'}), content_type='application/json')
    assert r.status_code == 401


def test_forgot_password_paths(client, monkeypatch):
    import app as app_module  # type: ignore
    # Lower rate limits to 1 to easily hit limit
    app_module.RATE_LIMIT_PER_IP_PER_HOUR = 1
    app_module.RATE_LIMIT_PER_EMAIL_PER_HOUR = 1

    # No email provided -> generic success
    r = client.post('/api/forgot-password', data=json.dumps({}), content_type='application/json', headers={'X-Forwarded-For': '9.9.9.9'})
    assert r.status_code == 200

    # Unknown email -> generic success
    r = client.post('/api/forgot-password', data=json.dumps({'email': 'none@example.com'}), content_type='application/json', headers={'X-Forwarded-For': '9.9.9.8'})
    assert r.status_code == 200

    # IP rate limit: two requests from same IP
    headers = {'X-Forwarded-For': '7.7.7.7'}
    r1 = client.post('/api/forgot-password', data=json.dumps({'email': 'x@example.com'}), content_type='application/json', headers=headers)
    r2 = client.post('/api/forgot-password', data=json.dumps({'email': 'y@example.com'}), content_type='application/json', headers=headers)
    assert r1.status_code == 200 and r2.status_code == 200

    # Email rate limit: two requests for same email
    headers = {'X-Forwarded-For': '8.8.8.8'}
    r1 = client.post('/api/forgot-password', data=json.dumps({'email': 'lim@example.com'}), content_type='application/json', headers=headers)
    r2 = client.post('/api/forgot-password', data=json.dumps({'email': 'lim@example.com'}), content_type='application/json', headers=headers)
    assert r1.status_code == 200 and r2.status_code == 200


def test_admin_cleanup_success(client, monkeypatch):
    import app as app_module  # type: ignore
    monkeypatch.setenv('ADMIN_TOKEN', 'secret')
    app_module.ADMIN_TOKEN = 'secret'

    # Create some old logs and tokens to be cleared
    from app import db, PasswordResetRequestLog, PasswordResetToken, User  # type: ignore
    with client.application.app_context():
        user = User(email_address='cleanup@example.com', full_name='C U', password_hash='x', country=None, newsletter_signup=False)
        db.session.add(user)
        db.session.commit()
        old_log = PasswordResetRequestLog(email='e@example.com', ip='1.1.1.1', created_at=datetime.utcnow() - timedelta(days=10))
        old_tok = PasswordResetToken(user_id=user.user_id, token='old', expires_at=datetime.utcnow() - timedelta(days=10), used=False, created_at=datetime.utcnow() - timedelta(days=10))
        db.session.add(old_log)
        db.session.add(old_tok)
        db.session.commit()

    r = client.post('/api/admin/maintenance/clear-reset-data', data=json.dumps({'days': 7}), content_type='application/json', headers={'X-Admin-Token': 'secret'})
    assert r.status_code == 200
    body = r.get_json()
    assert body.get('success') is True


def test_search_error_paths(client, monkeypatch):
    import app as app_module  # type: ignore

    # Service unavailable
    app_module.recipe_recommender = None
    r = client.get('/api/search')
    assert r.status_code == 500

    # recommend_recipes raises
    class BadRecommender:
        data = pd.DataFrame([])
        def recommend_recipes(self, *a, **k):
            raise RuntimeError('boom')
        def search_recipes(self, *a, **k):
            return self.data
    app_module.recipe_recommender = BadRecommender()
    r = client.get('/api/search', query_string={'complexity_score': 1})
    assert r.status_code == 500


def test_recipe_not_found_and_fallbacks(client, monkeypatch):
    # Recommender with minimal data that won't match
    class TinyRec:
        def __init__(self):
            self.data = pd.DataFrame([{ 'id': 1, 'name': 'Only' }])
    import app as app_module  # type: ignore
    app_module.recipe_recommender = TinyRec()

    r = client.get('/api/recipes/999')
    assert r.status_code == 404

    # Enriched-ingredients fallback using basic 'ingredients'
    df = pd.DataFrame([
        { 'id': 42, 'name': 'Basic', 'ingredients': '["1 cup sugar", "salt"]', 'steps': 'Mix.' }
    ])
    class Rec2:
        def __init__(self, data):
            self.data = data
    app_module.recipe_recommender = Rec2(df)
    r = client.get('/api/recipes/42/enriched-ingredients')
    assert r.status_code == 200
    data = r.get_json()
    assert len(data.get('parsedIngredients', [])) >= 1


def test_save_recipe_non_numeric_not_found(client, monkeypatch):
    # Set recommender with no matching recipe_id 'abc'
    df = pd.DataFrame([{ 'id': 1, 'name': 'Only' }])
    class Rec:
        def __init__(self, data):
            self.data = data
    import app as app_module  # type: ignore
    app_module.recipe_recommender = Rec(df)

    # Register/login
    r = client.post('/api/register', data=json.dumps({
        'email': 'savetest@example.com', 'password': 'pw', 'full_name': 'Save T'
    }), content_type='application/json')
    assert r.status_code == 200

    # Non-numeric id triggers ValueError in int casts and ultimately 400
    r = client.post('/api/saved-recipes', data=json.dumps({ 'recipe_id': 'abc' }), content_type='application/json')
    assert r.status_code == 400

