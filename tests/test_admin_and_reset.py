import json
from datetime import datetime, timedelta

import pytest


def test_admin_forbidden_when_no_token(client):
    r = client.get('/api/admin/status/email')
    assert r.status_code == 403
    r = client.get('/api/admin/rate-limit')
    assert r.status_code == 403


def test_admin_status_with_token(client, monkeypatch):
    import app as app_module  # type: ignore
    monkeypatch.setenv('ADMIN_TOKEN', 'secret')
    app_module.ADMIN_TOKEN = 'secret'

    r = client.get('/api/admin/status/email', headers={'X-Admin-Token': 'secret'})
    assert r.status_code == 200
    data = r.get_json()
    assert 'resend_available' in data

    r = client.get('/api/admin/rate-limit', headers={'X-Admin-Token': 'secret'}, query_string={'email': 'x@example.com', 'ip': '1.2.3.4'})
    assert r.status_code == 200


def test_reset_password_flow(client):
    # Register a user
    r = client.post('/api/register', data=json.dumps({
        'email': 'reset@example.com',
        'password': 'orig',
        'full_name': 'Reset Me',
    }), content_type='application/json')
    assert r.status_code == 200

    # Create a valid token row
    from app import db, User, PasswordResetToken  # type: ignore
    with client.application.app_context():
        user = User.query.filter_by(email_address='reset@example.com').first()
        assert user is not None
        token = PasswordResetToken(user_id=user.user_id, token='tok123', expires_at=datetime.utcnow() + timedelta(hours=1))
        db.session.add(token)
        db.session.commit()

    # Bad request body
    r = client.post('/api/reset-password', data=json.dumps({}), content_type='application/json')
    assert r.status_code == 400

    # Valid reset
    r = client.post('/api/reset-password', data=json.dumps({'token': 'tok123', 'password': 'newpass'}), content_type='application/json')
    assert r.status_code == 200
    assert r.get_json().get('success') is True

    # Invalid/expired token
    r = client.post('/api/reset-password', data=json.dumps({'token': 'tok123', 'password': 'again'}), content_type='application/json')
    assert r.status_code == 400

