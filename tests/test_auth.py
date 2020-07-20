import os
import pytest

from werkzeug.security import generate_password_hash

from director.models.users import User


def test_auth_enabled_not_authorized(enable_auth, client):
    resp = client.get("/api/workflows")
    assert resp.status_code == 401
    assert "unauthorized" in resp.json["error"]


def test_auth_enabled_authorized(enable_auth, client):
    user = User(username="test_user", password=generate_password_hash("root"))
    user.save()

    # Enc test_user:root = dGVzdF91c2VyOnJvb3Q=
    resp = client.get(
        "/api/workflows", headers={"Authorization": "Basic dGVzdF91c2VyOnJvb3Q="}
    )
    assert resp.status_code == 200


def test_auth_disabled(enable_auth, client):
    resp = client.get("/api/ping")
    assert resp.status_code == 200
    assert resp.json == {"message": "pong"}
