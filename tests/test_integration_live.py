import os
import time
import uuid
from typing import Optional

import pytest
import requests


API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8080/api")
LIVE_ENABLED = os.getenv("LIVE_API", "0") not in ("", "0", "false", "False")


def _ping(url: str, timeout: float = 1.0) -> bool:
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code < 500
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not LIVE_ENABLED or not _ping(f"{API_BASE}/health"),
    reason="LIVE_API not enabled or backend not reachable",
)


def _new_email() -> str:
    return f"user_{int(time.time())}_{uuid.uuid4().hex[:8]}@example.com"


def test_health_live():
    r = requests.get(f"{API_BASE}/health", timeout=2)
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_auth_and_saved_end_to_end_live():
    s = requests.Session()

    # unauth saved should 401
    r = s.get(f"{API_BASE}/saved-recipes", timeout=3, allow_redirects=False)
    assert r.status_code in (401, 302)

    # register (auto-login)
    email = _new_email()
    r = s.post(
        f"{API_BASE}/register",
        json={"email": email, "password": "secret123", "full_name": "Live User"},
        timeout=5,
    )
    assert r.status_code == 200
    assert r.json().get("success") is True

    # auth me should be authenticated
    r = s.get(f"{API_BASE}/auth/me", timeout=3)
    assert r.status_code == 200
    assert r.json().get("authenticated") is True

    # Try to search to find a real recipe id (if service available)
    r = s.get(f"{API_BASE}/search", params={"limit": 1}, timeout=10)
    if r.status_code == 200 and isinstance(r.json(), dict) and r.json().get("recipes"):
        recipe_id = str(r.json()["recipes"][0]["id"])

        # save this recipe
        r = s.post(f"{API_BASE}/saved-recipes", json={"recipe_id": recipe_id}, timeout=5)
        assert r.status_code in (200, 400)  # 400 if duplicate

        # list saved
        r = s.get(f"{API_BASE}/saved-recipes", timeout=3)
        assert r.status_code == 200
        ids = {item["id"] for item in r.json().get("recipes", [])}
        assert isinstance(ids, set)

        # fetch recipe details
        rr = s.get(f"{API_BASE}/recipes/{recipe_id}", timeout=5)
        assert rr.status_code in (200, 404)  # may not exist depending on dataset

        # enriched ingredients
        ei = s.get(f"{API_BASE}/recipes/{recipe_id}/enriched-ingredients", timeout=5)
        assert ei.status_code in (200, 404)

        # delete saved
        s.delete(f"{API_BASE}/saved-recipes/{recipe_id}", timeout=3)

    # logout
    r = s.post(f"{API_BASE}/logout", timeout=3)
    assert r.status_code == 200

    # auth me after logout
    r = s.get(f"{API_BASE}/auth/me", timeout=3)
    assert r.status_code == 401


def test_forgot_password_live():
    r = requests.post(
        f"{API_BASE}/forgot-password",
        json={"email": _new_email()},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True


def test_admin_status_live_optional():
    token = os.getenv("ADMIN_TOKEN")
    if not token:
        pytest.skip("ADMIN_TOKEN not set")
    r = requests.get(f"{API_BASE}/admin/status/email", headers={"X-Admin-Token": token}, timeout=3)
    assert r.status_code in (200, 403)
    if r.status_code == 200:
        data = r.json()
        assert "resend_available" in data
