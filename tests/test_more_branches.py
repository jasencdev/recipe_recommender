import json
import pandas as pd


def register_user(client, email='u@example.com'):
    r = client.post('/api/register', data=json.dumps({
        'email': email,
        'password': 'pw',
        'full_name': 'U'
    }), content_type='application/json')
    assert r.status_code == 200


def test_save_recipe_found_by_food_recipe_id(client, monkeypatch):
    # Recommender with food_recipe_id column
    df = pd.DataFrame([{
        'food_recipe_id': 500,
        'name': 'ViaFoodId',
        'minutes': 1,
        'difficulty': 'easy',
        'ingredients': '[]',
        'steps': ''
    }])
    class Rec:
        def __init__(self, data):
            self.data = data
    import app as app_module  # type: ignore
    app_module.recipe_recommender = Rec(df)

    register_user(client, 'foodid@example.com')
    r = client.post('/api/saved-recipes', data=json.dumps({'recipe_id': '500'}), content_type='application/json')
    assert r.status_code == 200


def test_save_recipe_found_by_string_recipe_id(client, monkeypatch):
    df = pd.DataFrame([{
        'recipe_id': 'RID-123',
        'name': 'ViaRecipeId',
        'minutes': 1,
        'difficulty': 'easy',
        'ingredients': '[]',
        'steps': ''
    }])
    class Rec:
        def __init__(self, data):
            self.data = data
    import app as app_module  # type: ignore
    app_module.recipe_recommender = Rec(df)

    register_user(client, 'rid@example.com')
    r = client.post('/api/saved-recipes', data=json.dumps({'recipe_id': 'RID-123'}), content_type='application/json')
    assert r.status_code == 200


def test_save_recipe_found_by_integer_index(client, monkeypatch):
    df = pd.DataFrame([{
        'name': 'ViaIdxInt',
        'minutes': 1,
        'difficulty': 'easy',
        'ingredients': '[]',
        'steps': ''
    }], index=[77])
    class Rec:
        def __init__(self, data):
            self.data = data
    import app as app_module  # type: ignore
    app_module.recipe_recommender = Rec(df)

    register_user(client, 'idxint@example.com')
    r = client.post('/api/saved-recipes', data=json.dumps({'recipe_id': '77'}), content_type='application/json')
    assert r.status_code == 200


def test_save_recipe_found_by_string_index(client, monkeypatch):
    df = pd.DataFrame([{
        'name': 'ViaIdxStr',
        'minutes': 1,
        'difficulty': 'easy',
        'ingredients': '[]',
        'steps': ''
    }], index=['key1'])
    class Rec:
        def __init__(self, data):
            self.data = data
    import app as app_module  # type: ignore
    app_module.recipe_recommender = Rec(df)

    register_user(client, 'idxstr@example.com')
    r = client.post('/api/saved-recipes', data=json.dumps({'recipe_id': 'key1'}), content_type='application/json')
    assert r.status_code == 200


def test_forgot_password_dev_token_path(client, monkeypatch):
    # Ensure a user exists
    client.post('/api/register', data=json.dumps({
        'email': 'dev@example.com', 'password': 'pw', 'full_name': 'Dev'
    }), content_type='application/json')

    # Force send_password_reset_email to return False and ENV != production
    import app as app_module  # type: ignore
    monkeypatch.setattr(app_module, 'ENVIRONMENT', 'development', raising=False)
    monkeypatch.setattr(app_module, 'send_password_reset_email', lambda *a, **k: False, raising=False)

    r = client.post('/api/forgot-password', data=json.dumps({'email': 'dev@example.com'}), content_type='application/json')
    assert r.status_code == 200
    body = r.get_json()
    # Should include devResetToken hint path
    assert body.get('success') is True and 'devResetToken' in body


def test_admin_cleanup_failure(client, monkeypatch):
    import app as app_module  # type: ignore
    monkeypatch.setenv('ADMIN_TOKEN', 'secret')
    app_module.ADMIN_TOKEN = 'secret'

    # Monkeypatch commit to raise to hit failure path
    from app import db  # type: ignore
    orig_commit = db.session.commit
    def boom():
        raise RuntimeError('fail')
    db.session.commit = boom  # type: ignore
    try:
        r = client.post('/api/admin/maintenance/clear-reset-data', data=json.dumps({'days': 7}), content_type='application/json', headers={'X-Admin-Token': 'secret'})
        assert r.status_code == 500
    finally:
        db.session.commit = orig_commit  # type: ignore


def test_reset_password_commit_failure(client, monkeypatch):
    # Setup user and token
    client.post('/api/register', data=json.dumps({
        'email': 'rp@example.com', 'password': 'pw', 'full_name': 'R'
    }), content_type='application/json')
    from app import db, User, PasswordResetToken  # type: ignore
    with client.application.app_context():
        user = User.query.filter_by(email_address='rp@example.com').first()
        token = PasswordResetToken(user_id=user.user_id, token='TK1', expires_at=pd.Timestamp.utcnow().to_pydatetime() + pd.Timedelta(hours=1).to_pytimedelta())
        db.session.add(token)
        db.session.commit()

    # Force commit failure on reset
    orig_commit = db.session.commit
    def boom():
        raise RuntimeError('fail')
    db.session.commit = boom  # type: ignore
    try:
        r = client.post('/api/reset-password', data=json.dumps({'token': 'TK1', 'password': 'new'}), content_type='application/json')
        assert r.status_code == 500
    finally:
        db.session.commit = orig_commit  # type: ignore

