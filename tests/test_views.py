def test_view(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert not resp.is_json
    assert resp.mimetype == "text/html"
    assert "<title>Celery Director</title>" in str(resp.data)


def test_404_view(client):
    resp = client.get("/notfound")
    assert resp.status_code == 404
    assert not resp.is_json
    assert resp.mimetype == "text/html"
    assert "<title>404 Not Found</title>" in str(resp.data)


def test_api(client):
    resp = client.get("/api/ping")
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.mimetype == "application/json"
    assert resp.json == {"message": "pong"}


def test_404_api(client):
    resp = client.get("/api/notfound")
    assert resp.status_code == 404
    assert resp.is_json
    assert resp.mimetype == "application/json"
    assert "The requested URL was not found" in resp.json["error"]
