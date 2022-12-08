from uuid import UUID

import pytest

from director.exceptions import WorkflowNotFound
from director.tasks.workflows import start, end
from director.models.tasks import Task
from director.models.workflows import Workflow

from tests.conftest import _remove_keys


def test_create_unknown_workflow(create_builder):
    with pytest.raises(WorkflowNotFound):
        create_builder("project", "UNKNOW_WORKFLOW", {})


def test_build_one_task(create_builder):
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
    keys = ["id", "created", "updated", "task", "is_hook"]
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
    }
    assert _remove_keys(tasks[1].to_dict(), keys) == {
        "key": "TASK_B",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
    }

    assert _remove_keys(tasks[2].to_dict(), keys) == {
        "key": "TASK_C",
        "previous": [str(tasks[1].to_dict()["id"])],
        "result": None,
        "status": "pending",
    }


def test_build_grouped_tasks(app, create_builder):
    keys = ["id", "created", "updated", "task", "is_hook"]
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
    }
    assert _remove_keys(tasks[1].to_dict(), keys) == {
        "key": "TASK_B",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
    }
    assert _remove_keys(tasks[2].to_dict(), keys) == {
        "key": "TASK_C",
        "previous": [str(tasks[0].to_dict()["id"])],
        "result": None,
        "status": "pending",
    }


def test_build_tasks_with_routing(create_builder):
    data, builder = create_builder("example", "TASK_ROUTING", {"foo": "bar"})

    assert len(builder.canvas) == 4
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"

    # Checl the task queues in canvas
    assert builder.canvas[1].task == "TASK_A"
    assert builder.canvas[1].options["queue"] == "q1"

    assert builder.canvas[2].task == "celery.group"
    group_tasks = builder.canvas[2].tasks
    assert len(group_tasks) == 2

    assert group_tasks[0].task == "TASK_B"
    assert group_tasks[1].task == "TASK_C"

    assert group_tasks[0].options["queue"] == "q2"
    assert group_tasks[1].options["queue"] == "q1"


def test_build_tasks_with_successandfailure_hooks(app, create_builder):
    keys = ["id", "created", "updated", "task"]
    data, builder = create_builder("example", "SUCCESSANDFAILURE_HOOK", {})

    assert len(builder.canvas) == 3
    assert len(builder.failure_hook_canvas) == 1
    assert len(builder.success_hook_canvas) == 1

    # Check the tasks in database (including previouses ID)
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 2  # Only success hook is registered when not triggerred
    assert _remove_keys(tasks[0].to_dict(), keys) == {
        "key": "TASK_A",
        "previous": [],
        "result": None,
        "status": "pending",
        "is_hook": False,
    }
    assert _remove_keys(tasks[1].to_dict(), keys) == {
        "key": "TASK_B",
        "previous": [],
        "result": None,
        "status": "pending",
        "is_hook": True,
    }
