from pathlib import Path

import pytest
from celery.canvas import _chain
from celery.contrib.testing import worker
from flask import Response
from flask.testing import FlaskClient

from director import create_app
from director.builder import WorkflowBuilder
from director.extensions import cel, db
from director.models.workflows import Workflow


KEYS_TO_REMOVE = ["id", "created", "updated"]


class DirectorTestClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        super(DirectorTestClient, self).__init__(*args, **kwargs)


def _remove_keys(d, keys=KEYS_TO_REMOVE):
    if isinstance(keys, str):
        keys = [keys]
    if isinstance(d, dict):
        for key in set(keys):
            if key in d:
                del d[key]
        for k, v in d.items():
            _remove_keys(v, keys)
    elif isinstance(d, list):
        for i in d:
            _remove_keys(i, keys)
    return d


class DirectorResponse(Response):
    _KEYS_TO_REMOVE = KEYS_TO_REMOVE

    @property
    def json(self):
        return _remove_keys(self.get_json(), self._KEYS_TO_REMOVE)


@pytest.fixture(scope="module")
def app_module():
    app = create_app(str(Path(__file__).parent.resolve() / "workflows"))

    with app.app_context():
        db.create_all()

    app.response_class = DirectorResponse
    app.test_client_class = DirectorTestClient
    yield app

    with app.app_context():
        db.drop_all()

    return app_module


@pytest.fixture(scope="function")
def app(app_module):
    with app_module.app_context():

        # Clean the relational database
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

    return app_module


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def enable_auth(app):
    with app.app_context():
        app.config["AUTH_ENABLED"] = True

    return app


@pytest.fixture(scope="function")
def no_worker(monkeypatch):
    monkeypatch.setattr(_chain, "apply_async", lambda x: None)


@pytest.fixture(scope="function")
def create_builder(app):
    def _create_builder(project, name, payload, periodic=False, keys=KEYS_TO_REMOVE):
        with app.app_context():
            obj = Workflow(
                project=project, name=name, payload=payload, periodic=periodic
            )
            obj.save()
            data = obj.to_dict()
            wf = WorkflowBuilder(obj.id)
            wf.build()
        return _remove_keys(data), wf

    return _create_builder
