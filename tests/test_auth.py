import os

from werkzeug.security import generate_password_hash

from director.models.users import User


def test_auth_enabled_not_authorized(app, client):
    with app.app_context():
        app.config["AUTH_ENABLED"] = True
        resp = client.get("/api/ping")
        assert resp.status_code == 401
        assert (
            "The server could not verify that you are authorized" in resp.json["error"]
        )


def test_auth_enabled_authorized(app, client):
    user = User(username="test_user", password=generate_password_hash("root"))
    user.save()

    # Enc test_user:root = dGVzdF91c2VyOnJvb3Q=
    resp = client.get(
        "/api/ping", headers={"Authorization": "Basic dGVzdF91c2VyOnJvb3Q="}
    )
    assert resp.status_code == 200
    assert resp.json == {"message": "pong"}


def test_auth_desabled(app, client):
    with app.app_context():
        app.config["AUTH_ENABLED"] = False
        resp = client.get("/api/ping")
        assert resp.status_code == 200
        assert resp.json == {"message": "pong"}
