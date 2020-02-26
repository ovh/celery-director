from unittest.mock import PropertyMock, patch

import pytest
from director.exceptions import WorkflowNotFound
from director.models.workflows import Workflow
from director.models.tasks import Task


DEFAULT_PAYLOAD = {"project": "example", "name": "WORKFLOW", "payload": {}}


def test_pong(client):
    resp = client.get("/api/ping")
    assert resp.status_code == 200
    assert resp.json == {"message": "pong"}


def test_post_workflow_without_payload(client, no_worker):
    resp = client.post("/api/workflows", json=DEFAULT_PAYLOAD)
    assert resp.status_code == 201
    assert resp.json == {
        "fullname": "example.WORKFLOW",
        "name": "WORKFLOW",
        "payload": {},
        "periodic": False,
        "project": "example",
        "status": "pending",
    }


def test_post_workflow_with_payload(client, no_worker):
    payload = {**DEFAULT_PAYLOAD}
    payload["payload"] = {"nested": {"foo": "bar"}}
    resp = client.post("/api/workflows", json=payload)
    assert resp.status_code == 201
    assert resp.json == {
        "fullname": "example.WORKFLOW",
        "name": "WORKFLOW",
        "payload": {"nested": {"foo": "bar"}},
        "periodic": False,
        "project": "example",
        "status": "pending",
    }


def test_post_workflow_required_props(client):
    resp = client.post("/api/workflows", json={})
    assert resp.status_code == 400
    assert resp.json["error"] == "Error validating against schema"
    assert len(resp.json["errors"]) == 3
    for prop in ["project", "name", "payload"]:
        assert f"{prop}" in " ".join(resp.json["errors"])

    resp = client.post("/api/workflows", json={"project": "example"})
    assert resp.status_code == 400
    assert len(resp.json["errors"]) == 2
    for prop in ["name", "payload"]:
        assert f"{prop}" in " ".join(resp.json["errors"])

    resp = client.post(
        "/api/workflows", json={"project": "example", "name": "WORKFLOW"}
    )
    assert resp.status_code == 400
    assert len(resp.json["errors"]) == 1
    assert "payload" in resp.json["errors"][0]


def test_post_workflow_unexpected_properties(client):
    payload = {**DEFAULT_PAYLOAD, "foo": "bar"}
    resp = client.post("/api/workflows", json=payload)
    assert resp.status_code == 400
    assert resp.json["error"] == "Error validating against schema"
    assert "'foo' was unexpected" in resp.json["errors"][0]


def test_relaunch_not_existing_workflow(client):
    resp = client.post(
        "/api/workflows/280d0c4065d04063a800a3b674562711/relaunch", json={}
    )
    assert resp.status_code == 404


def test_relaunch_workflow(client, no_worker):
    payload = {**DEFAULT_PAYLOAD}
    payload["payload"] = {"nested": {"foo": "bar"}}
    resp = client.post("/api/workflows", json=payload)
    with patch("tests.conftest.DirectorResponse._KEYS_TO_REMOVE", new=[]):
        workflow_id = resp.json["id"]
    assert resp.status_code == 201

    resp = client.post(f"/api/workflows/{workflow_id}/relaunch", json={})
    assert resp.status_code == 201
    assert resp.json == {
        "fullname": "example.WORKFLOW",
        "name": "WORKFLOW",
        "payload": {"nested": {"foo": "bar"}},
        "periodic": False,
        "project": "example",
        "status": "pending",
    }

    # workflows are the same
    resp = client.get("/api/workflows")
    assert len(resp.json) == 2
    del resp.json[0]["status"]
    del resp.json[1]["status"]
    assert resp.json[0] == resp.json[1]

    # tasks are the same
    resp = client.get("/api/workflows")
    with patch("tests.conftest.DirectorResponse._KEYS_TO_REMOVE", new=[]):
        workflows = resp.json
    tasks1 = [
        t["key"]
        for t in client.get(f"/api/workflows/{workflows[0]['id']}").json.get("tasks")
    ]
    tasks2 = [
        t["key"]
        for t in client.get(f"/api/workflows/{workflows[1]['id']}").json.get("tasks")
    ]
    assert tasks1 == tasks2


def test_not_found_workflows(client, no_worker):
    resp = client.post("/api/workflows", json=DEFAULT_PAYLOAD)
    assert resp.status_code == 201

    payload = {**DEFAULT_PAYLOAD}
    payload["name"] = "NOT_FOUND"
    resp = client.post("/api/workflows", json=payload)
    assert resp.status_code == 404
    assert resp.json == {"error": "Workflow example.NOT_FOUND not found"}

    payload = {**DEFAULT_PAYLOAD}
    payload["project"] = "NOT_FOUND"
    resp = client.post("/api/workflows", json=payload)
    assert resp.status_code == 404
    assert resp.json == {"error": "Workflow NOT_FOUND.WORKFLOW not found"}


def test_list_workflows(client, no_worker):
    resp = client.get("/api/workflows")
    assert resp.status_code == 200
    assert resp.json == []

    resp = client.post("/api/workflows", json=DEFAULT_PAYLOAD)
    assert resp.status_code == 201

    resp = client.get("/api/workflows")
    assert resp.json == [
        {
            "fullname": "example.WORKFLOW",
            "name": "WORKFLOW",
            "payload": {},
            "periodic": False,
            "project": "example",
            "status": "pending",
        }
    ]

    for i in range(9):
        client.post("/api/workflows", json=DEFAULT_PAYLOAD)
    resp = client.get("/api/workflows")
    assert len(resp.json) == 10


def test_get_workflow(client, no_worker):
    resp = client.post("/api/workflows", json=DEFAULT_PAYLOAD)
    with patch("tests.conftest.DirectorResponse._KEYS_TO_REMOVE", new=[]):
        workflow_id = resp.json["id"]

    resp = client.get(f"/api/workflows/{workflow_id}")
    assert resp.status_code == 200
    assert len(resp.json["tasks"]) == 1

    del resp.json["tasks"][0]["task"]
    assert resp.json == {
        "fullname": "example.WORKFLOW",
        "name": "WORKFLOW",
        "payload": {},
        "periodic": False,
        "project": "example",
        "status": "pending",
        "tasks": [{"key": "TASK_EXAMPLE", "previous": [], "status": "pending",}],
    }


@patch("tests.conftest.DirectorResponse._KEYS_TO_REMOVE", new=[])
def test_get_workflow_simple_chain(client, no_worker):
    payload = {**DEFAULT_PAYLOAD}
    payload["name"] = "SIMPLE_CHAIN"
    workflow_id = client.post("/api/workflows", json=payload).json["id"]

    resp = client.get(f"/api/workflows/{workflow_id}")
    assert resp.status_code == 200
    assert len(resp.json["tasks"]) == 3


def test_get_not_found_workflow(client):
    resp = client.get("/api/workflows/e0ee42d8-e00f-4557-8f75-781106dbbea4")
    assert resp.status_code == 404


def test_schema(client, no_worker):
    payload = {"project": "schemas", "name": "SIMPLE_SCHEMA", "payload": {}}
    resp = client.post("/api/workflows", json=payload)
    assert resp.status_code == 400
    assert resp.json == {
        "error": "Payload is not valid",
        "errors": ["'name' is a required property"],
    }

    payload["payload"]["price"] = "foo"
    resp = client.post("/api/workflows", json=payload)
    assert resp.status_code == 400
    assert resp.json["error"] == "Payload is not valid"
    assert sorted(resp.json["errors"]) == sorted(
        ["'name' is a required property", "'foo' is not of type 'number'"]
    )

    payload["payload"] = {"name": "foo", "price": 100}
    resp = client.post("/api/workflows", json=payload)
    assert resp.status_code == 201
