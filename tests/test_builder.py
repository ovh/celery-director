from uuid import UUID

import pytest

from director.exceptions import WorkflowNotFound
from director.tasks.workflows import start, end
from director.models.tasks import Task
from director.models.workflows import Workflow
from director.settings import Config

from tests.conftest import _remove_keys


def test_create_unknown_workflow(app, create_builder):
    with pytest.raises(WorkflowNotFound):
        create_builder("project", "UNKNOW_WORKFLOW", {})


def test_build_one_task(app, create_builder):
    data, builder = create_builder("example", "WORKFLOW", {"foo": "bar"})
    assert data == {
        "name": "WORKFLOW",
        "payload": {"foo": "bar"},
        "project": "example",
        "fullname": "example.WORKFLOW",
        "status": "pending",
        "periodic": False,
    }

    assert len(builder.canvas) == 3
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert builder.canvas[1].task == "TASK_EXAMPLE"


def test_build_chained_tasks(app, create_builder):
    keys = ["id", "created", "updated", "task"]
    data, builder = create_builder("example", "SIMPLE_CHAIN", {"foo": "bar"})
    assert data == {
        "name": "SIMPLE_CHAIN",
        "payload": {"foo": "bar"},
        "project": "example",
        "fullname": "example.SIMPLE_CHAIN",
        "status": "pending",
        "periodic": False,
    }

    # Check the Celery canvas
    assert len(builder.canvas) == 5
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert builder.canvas[1].task == "TASK_A"
    assert builder.canvas[2].task == "TASK_B"
    assert builder.canvas[3].task == "TASK_C"

    # Check the tasks in database (including previouses ID)
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 3
    assert _remove_keys(tasks[0].to_dict(), keys) == {
        "key": "TASK_A",
        "previous": [],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }
    assert _remove_keys(tasks[1].to_dict(), keys) == {
        "key": "TASK_B",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }

    assert _remove_keys(tasks[2].to_dict(), keys) == {
        "key": "TASK_C",
        "previous": [str(tasks[1].to_dict()["id"])],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }


def test_build_grouped_tasks(app, create_builder):
    keys = ["id", "created", "updated", "task"]
    data, builder = create_builder("example", "SIMPLE_GROUP", {"foo": "bar"})
    assert data == {
        "name": "SIMPLE_GROUP",
        "payload": {"foo": "bar"},
        "project": "example",
        "fullname": "example.SIMPLE_GROUP",
        "status": "pending",
        "periodic": False,
    }

    # Check the Celery canvas
    assert len(builder.canvas) == 4
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert builder.canvas[1].task == "TASK_A"
    assert builder.canvas[2].task == "celery.group"
    group_tasks = builder.canvas[2].tasks
    assert len(group_tasks) == 2
    assert [group_tasks[0].task, group_tasks[1].task] == [
        "TASK_B",
        "TASK_C",
    ]

    # Check the tasks in database (including previouses ID)
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 3
    assert _remove_keys(tasks[0].to_dict(), keys) == {
        "key": "TASK_A",
        "previous": [],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }
    assert _remove_keys(tasks[1].to_dict(), keys) == {
        "key": "TASK_B",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }
    assert _remove_keys(tasks[2].to_dict(), keys) == {
        "key": "TASK_C",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }


def test_build_complex_workflow(app, create_builder):
    keys = ["id", "created", "updated", "task"]
    data, builder = create_builder("example", "COMPLEX_WORKFLOW", {"foo": "bar"})
    assert data == {
        "name": "COMPLEX_WORKFLOW",
        "payload": {"foo": "bar"},
        "project": "example",
        "fullname": "example.COMPLEX_WORKFLOW",
        "status": "pending",
        "periodic": False,
    }

    # Check the Celery canvas
    assert len(builder.canvas) == 5
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert builder.canvas[1].task == "TASK_EXAMPLE"
    assert builder.canvas[2].task == "celery.group"
    assert builder.canvas[3].task == "TASK_EXAMPLE"

    group_tasks = builder.canvas[2].tasks
    group_tasks_names = [t.task for t in group_tasks]
    assert group_tasks_names == ["TASK_A", "TASK_B", "TASK_C"]

    # Check the Celery Canvas Options
    assert builder.canvas[0].options["queue"] == "celery"
    assert group_tasks[0].options["queue"] == "complex"
    assert group_tasks[0].options["retries"] == 3
    assert group_tasks[-1].options.get("retries") is None
    assert group_tasks[-1].options["queue"] == "celery"
    assert builder.canvas[3].options["queue"] == "complex"
    assert builder.canvas[3].options["retries"] == 5

    # Check the tasks in database (including previouses ID)
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()

    assert len(tasks) == 5
    assert _remove_keys(tasks[0].to_dict(), keys) == {
        "key": "TASK_EXAMPLE",
        "previous": [],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }
    assert _remove_keys(tasks[1].to_dict(), keys) == {
        "key": "TASK_A",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
        "queue": "complex",
    }
    assert _remove_keys(tasks[2].to_dict(), keys) == {
        "key": "TASK_B",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }
    assert _remove_keys(tasks[3].to_dict(), keys) == {
        "key": "TASK_C",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
        "queue": "celery",
    }
    assert _remove_keys(tasks[4].to_dict(), keys) == {
        "key": "TASK_EXAMPLE",
        "previous": [str(t.id) for t in tasks[1:4]],
        "result": None,
        "status": "pending",
        "queue": "complex",
    }
