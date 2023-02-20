import time

import pytest
from celery.result import GroupResult
from celery.schedules import crontab
from kombu.exceptions import EncodeError

from director import build_celery_schedule
from director.exceptions import WorkflowSyntaxError
from director.models.tasks import Task
from director.models.workflows import Workflow
from director.builder import WorkflowBuilder


KEYS = ["id", "created", "updated", "task"]


def test_execute_one_task_success(app, create_builder):
    workflow, builder = create_builder("example", "WORKFLOW", {})
    assert workflow["status"] == "pending"

    # Canvas has been built
    assert len(builder.canvas) == 3
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert builder.canvas[1].task == "TASK_EXAMPLE"

    # Tasks added in DB
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 1
    assert tasks[0].key == "TASK_EXAMPLE"
    assert tasks[0].status.value == "pending"

    # Tasks executed in Celery
    result = builder.run()
    assert result.get() is None
    assert result.parent.parent.get() is None
    assert result.parent.get() == "task_example"
    assert result.parent.state == "SUCCESS"

    # DB rows status updated
    time.sleep(0.5)
    with app.app_context():
        task = Task.query.filter_by(id=tasks[0].id).first()
        workflow = Workflow.query.filter_by(id=task.workflow_id).first()
    assert workflow.status.value == "success"
    assert task.status.value == "success"


def test_execute_one_task_error(app, create_builder):
    workflow, builder = create_builder("example", "ERROR", {})
    assert workflow["status"] == "pending"

    # Canvas has been built
    assert len(builder.canvas) == 3
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert builder.canvas[1].task == "TASK_ERROR"

    # Tasks added in DB
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 1
    assert tasks[0].key == "TASK_ERROR"
    assert tasks[0].status.value == "pending"

    # Tasks executed in Celery
    result = builder.run()
    with pytest.raises(ZeroDivisionError):
        assert result.get()

    # DB rows status updated
    time.sleep(0.5)
    with app.app_context():
        task = Task.query.filter_by(id=tasks[0].id).first()
        workflow = Workflow.query.filter_by(id=task.workflow_id).first()
    assert workflow.status.value == "error"
    assert task.status.value == "error"


def test_execute_chain_success(app, create_builder):
    workflow, builder = create_builder("example", "SIMPLE_CHAIN", {})
    assert workflow["status"] == "pending"

    # Canvas has been built
    assert len(builder.canvas) == 5
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert [c.task for c in builder.canvas[1:-1]] == ["TASK_A", "TASK_B", "TASK_C"]

    # Tasks added in DB
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 3
    assert [n.key for n in tasks] == ["TASK_A", "TASK_B", "TASK_C"]
    assert set([n.status.value for n in tasks]) == {
        "pending",
    }

    # Tasks executed in Celery
    result = builder.run()
    assert result.get() is None
    assert result.parent.parent.parent.parent.get() is None
    assert result.parent.get() == "task_c"
    assert result.parent.state == "SUCCESS"
    assert result.parent.parent.get() == "task_b"
    assert result.parent.parent.state == "SUCCESS"
    assert result.parent.parent.parent.get() == "task_a"
    assert result.parent.parent.parent.state == "SUCCESS"

    # DB rows status updated
    time.sleep(0.5)
    with app.app_context():
        tasks = Task.query.filter_by(id=tasks[0].id).all()
        workflow = Workflow.query.filter_by(id=tasks[0].workflow_id).first()
    assert workflow.status.value == "success"

    for task in tasks:
        assert task.status.value == "success"


def test_execute_chain_error(app, create_builder):
    workflow, builder = create_builder("example", "SIMPLE_CHAIN_ERROR", {})
    assert workflow["status"] == "pending"

    # Canvas has been built
    assert len(builder.canvas) == 5
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert [c.task for c in builder.canvas[1:-1]] == ["TASK_A", "TASK_B", "TASK_ERROR"]

    # Tasks added in DB
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 3
    assert [n.key for n in tasks] == ["TASK_A", "TASK_B", "TASK_ERROR"]
    assert set([n.status.value for n in tasks]) == {
        "pending",
    }

    # Tasks executed in Celery
    result = builder.run()
    with pytest.raises(ZeroDivisionError):
        assert result.get()

    # DB rows status updated
    time.sleep(0.5)
    with app.app_context():
        task_a = Task.query.filter_by(key="TASK_A").first()
        task_b = Task.query.filter_by(key="TASK_B").first()
        task_error = Task.query.filter_by(key="TASK_ERROR").first()
        workflow = Workflow.query.filter_by(id=task_a.workflow_id).first()
    assert task_a.status.value == "success"
    assert task_b.status.value == "success"
    assert task_error.status.value == "error"
    assert workflow.status.value == "error"


def test_execute_group_success(app, create_builder):
    workflow, builder = create_builder("example", "SIMPLE_GROUP", {})
    assert workflow["status"] == "pending"

    # Canvas has been built
    assert len(builder.canvas) == 4
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert builder.canvas[1].task == "TASK_A"
    group_tasks = builder.canvas[2].tasks
    assert len(group_tasks) == 2
    assert [group_tasks[0].task, group_tasks[1].task] == [
        "TASK_B",
        "TASK_C",
    ]

    # Tasks added in DB
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 3
    assert [n.key for n in tasks] == ["TASK_A", "TASK_B", "TASK_C"]
    assert set([n.status.value for n in tasks]) == {
        "pending",
    }

    # Tasks executed in Celery
    result = builder.run()
    assert result.get() is None
    assert result.parent.parent.get() == "task_a"
    assert isinstance(result.parent, GroupResult)
    assert result.parent.get() == ["task_b", "task_c"]

    # DB rows status updated
    time.sleep(0.5)
    with app.app_context():
        tasks = Task.query.filter_by(id=tasks[0].id).all()
        workflow = Workflow.query.filter_by(id=tasks[0].workflow_id).first()
    assert workflow.status.value == "success"

    for task in tasks:
        assert task.status.value == "success"


def test_execute_group_error(app, create_builder):
    workflow, builder = create_builder("example", "SIMPLE_GROUP_ERROR", {})
    assert workflow["status"] == "pending"

    # Canvas has been built
    assert len(builder.canvas) == 4
    assert builder.canvas[0].task == "director.tasks.workflows.start"
    assert builder.canvas[-1].task == "director.tasks.workflows.end"
    assert builder.canvas[1].task == "TASK_A"
    group_tasks = builder.canvas[2].tasks
    assert len(group_tasks) == 2
    assert [group_tasks[0].task, group_tasks[1].task] == ["TASK_ERROR", "TASK_C"]

    # Tasks added in DB
    with app.app_context():
        tasks = Task.query.order_by(Task.created_at.asc()).all()
    assert len(tasks) == 3
    assert [n.key for n in tasks] == ["TASK_A", "TASK_ERROR", "TASK_C"]
    assert set([n.status.value for n in tasks]) == {
        "pending",
    }

    # Tasks executed in Celery
    result = builder.run()
    with pytest.raises(ZeroDivisionError):
        assert result.get()

    # DB rows status updated
    time.sleep(0.5)
    with app.app_context():
        task_a = Task.query.filter_by(key="TASK_A").first()
        task_error = Task.query.filter_by(key="TASK_ERROR").first()
        task_c = Task.query.filter_by(key="TASK_C").first()
        workflow = Workflow.query.filter_by(id=task_a.workflow_id).first()
    assert task_a.status.value == "success"
    assert task_error.status.value == "error"
    assert task_c.status.value == "success"
    assert workflow.status.value == "error"


@pytest.mark.skip_no_worker()
def test_execute_celery_error_one_task(app, create_builder):
    workflow, builder = create_builder("example", "CELERY_ERROR_ONE_TASK", {})
    assert workflow["status"] == "pending"

    # Tasks executed in Celery
    result = builder.run()
    with pytest.raises(EncodeError):
        assert result.get()

    # DB rows status updated
    time.sleep(0.5)
    with app.app_context():
        task = Task.query.order_by(Task.created_at.asc()).first()
        workflow = Workflow.query.filter_by(id=task.workflow_id).first()
    assert workflow.status.value == "error"
    assert task.status.value == "error"


@pytest.mark.skip_no_worker()
def test_execute_celery_error_multiple_tasks(app, create_builder):
    workflow, builder = create_builder("example", "CELERY_ERROR_MULTIPLE_TASKS", {})
    assert workflow["status"] == "pending"

    # Tasks executed in Celery
    result = builder.run()
    with pytest.raises(EncodeError):
        assert result.get()

    # DB rows status updated
    time.sleep(0.5)
    with app.app_context():
        task_a = Task.query.filter_by(key="TASK_A").first()
        task_celery_error = Task.query.filter_by(key="TASK_CELERY_ERROR").first()
        workflow = Workflow.query.filter_by(id=task_a.workflow_id).first()
    assert task_a.status.value == "success"
    assert task_celery_error.status.value == "error"
    assert workflow.status.value == "error"


@pytest.mark.skip_no_worker()
def test_cancel_workflow(app):

    with app.app_context():
        workflow = Workflow(
            project="example", name="DELAY_TASK", payload={}, periodic=False
        )
        workflow.save()
        builder = WorkflowBuilder(workflow.id)
        builder.build()
        assert workflow.status.value == "pending"

        # Tasks executed in Celery
        builder.run()

        # DB rows status updated
        time.sleep(1)

        workflow = Workflow.query.filter_by(id=workflow.id).first()

        assert workflow.tasks[0].status.value == "progress"

        builder.cancel()

        # DB rows status updated
        time.sleep(5)

        workflow = Workflow.query.filter_by(id=workflow.id).first()

        assert workflow.status.value == "canceled"
        assert workflow.tasks[0].status.value == "canceled"

        # Wait for the restart of the only prefork
        time.sleep(1)


def test_return_values(app, create_builder):
    workflow, builder = create_builder("example", "RETURN_VALUES", {})
    builder.run()

    time.sleep(0.5)

    with app.app_context():
        tasks = {t.key: t.result for t in Task.query.all()}

    assert tasks["STR"] == "return_value"
    assert tasks["INT"] == 1234
    assert tasks["LIST"] == ["jack", "sape", "guido"]
    assert tasks["NONE"] is None
    assert tasks["DICT"] == {"foo": "bar"}
    assert tasks["NESTED"] == {
        "jack": 4098,
        "sape": 4139,
        "guido": 4127,
        "nested": {"foo": "bar"},
        "none": None,
        "list": ["jack", "sape", "guido"],
    }


@pytest.mark.skip_no_worker()
def test_execute_workflow_withfailurehook(app):

    with app.app_context():
        workflow = Workflow(
            project="example", name="FAILURE_HOOK", payload={}, periodic=False
        )
        workflow.save()
        workflow_id = workflow.id
        builder = WorkflowBuilder(workflow.id)
        builder.build()
        assert workflow.status.value == "pending"

        # Tasks executed in Celery
        result = builder.run()
        with pytest.raises(ZeroDivisionError):
            assert result.get()

    # DB rows status updated
    time.sleep(0.5)

    with app.app_context():
        workflow = Workflow.query.filter_by(id=workflow_id).first()

        assert workflow.status.value == "error"
        assert workflow.tasks[0].status.value == "success"
        assert workflow.tasks[1].status.value == "error"
        assert workflow.tasks[2].status.value == "success"


@pytest.mark.skip_no_worker()
def test_execute_workflow_withsuccesshook(app):

    with app.app_context():
        workflow = Workflow(
            project="example", name="SUCCESSANDFAILURE_HOOK", payload={}, periodic=False
        )
        workflow.save()
        workflow_id = workflow.id
        builder = WorkflowBuilder(workflow.id)
        builder.build()
        assert workflow.status.value == "pending"

        # Tasks executed in Celery
        result = builder.run()
        assert result.get() == None

    # DB rows status updated
    time.sleep(0.5)

    with app.app_context():
        workflow = Workflow.query.filter_by(id=workflow_id).first()

        assert workflow.status.value == "success"
        assert workflow.tasks[0].status.value == "success"
        assert workflow.tasks[1].status.value == "success"


def test_return_exception(app, create_builder):
    workflow, builder = create_builder("example", "RETURN_EXCEPTION", {})
    builder.run()

    time.sleep(0.5)
    with app.app_context():
        tasks = {t.key: t.result for t in Task.query.all()}

    assert tasks["STR"] == "return_value"
    assert list(tasks["TASK_ERROR"].keys()) == ["exception", "traceback"]
    assert tasks["TASK_ERROR"]["exception"] == "division by zero"
    assert tasks["TASK_ERROR"]["traceback"].startswith(
        "Traceback (most recent call last)"
    )
    assert "ZeroDivisionError: division by zero" in tasks["TASK_ERROR"]["traceback"]


def test_build_celery_schedule_float_with_payload():
    float_schedule = {"payload": {}, "schedule": 30.0}
    assert ("30.0", 30.0) == build_celery_schedule(
        "workflow_schedule_float", float_schedule
    )


def test_build_celery_schedule_float():
    float_schedule = {"schedule": 30.0}
    assert ("30.0", 30.0) == build_celery_schedule(
        "workflow_schedule_float", float_schedule
    )


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "1 * * * *",
            crontab(
                minute="1",
                hour="*",
                day_of_week="*",
                day_of_month="*",
                month_of_year="*",
            ),
        ),
        (
            "* 1 * * *",
            crontab(
                minute="*",
                hour="1",
                day_of_week="*",
                day_of_month="*",
                month_of_year="*",
            ),
        ),
        (
            "* * 1 * *",
            crontab(
                minute="*",
                hour="*",
                day_of_week="1",
                day_of_month="*",
                month_of_year="*",
            ),
        ),
        (
            "* * * 1 *",
            crontab(
                minute="*",
                hour="*",
                day_of_week="*",
                day_of_month="1",
                month_of_year="*",
            ),
        ),
        (
            "* * * * 1",
            crontab(
                minute="*",
                hour="*",
                day_of_week="*",
                day_of_month="*",
                month_of_year="1",
            ),
        ),
        (
            "*/10 */11 */12 */13 */14",
            crontab(
                minute="*/10",
                hour="*/11",
                day_of_week="*/12",
                day_of_month="*/13",
                month_of_year="*/14",
            ),
        ),
    ],
)
def test_build_celery_schedule_crontab(test_input, expected):
    cron_schedule = {"schedule": test_input}
    assert (test_input, expected) == build_celery_schedule(
        "workflow_crontab", cron_schedule
    )


def test_build_celery_interval():
    float_schedule = {"interval": 30.0}
    assert ("30.0", 30.0) == build_celery_schedule(
        "workflow_schedule_float", float_schedule
    )


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "1 * * * *",
            crontab(
                minute="1",
                hour="*",
                day_of_month="*",
                month_of_year="*",
                day_of_week="*",
            ),
        ),
        (
            "* 1 * * *",
            crontab(
                minute="*",
                hour="1",
                day_of_month="*",
                month_of_year="*",
                day_of_week="*",
            ),
        ),
        (
            "* * 1 * *",
            crontab(
                minute="*",
                hour="*",
                day_of_month="1",
                month_of_year="*",
                day_of_week="*",
            ),
        ),
        (
            "* * * 1 *",
            crontab(
                minute="*",
                hour="*",
                day_of_month="*",
                month_of_year="1",
                day_of_week="*",
            ),
        ),
        (
            "* * * * 1",
            crontab(
                minute="*",
                hour="*",
                day_of_month="*",
                month_of_year="*",
                day_of_week="1",
            ),
        ),
        (
            "*/10 */11 */12 */13 */14",
            crontab(
                minute="*/10",
                hour="*/11",
                day_of_month="*/12",
                month_of_year="*/13",
                day_of_week="*/14",
            ),
        ),
    ],
)
def test_build_celery_crontab(test_input, expected):
    cron_schedule = {"crontab": test_input}
    assert (test_input, expected) == build_celery_schedule(
        "workflow_crontab", cron_schedule
    )


def test_build_celery_invalid_crontab():
    # missing one element on the crontab syntax
    periodic_conf = {"crontab": "* * * *"}
    with pytest.raises(WorkflowSyntaxError):
        build_celery_schedule("workflow_invalid_crontab", periodic_conf)


def test_build_celery_invalid_schedule():
    cron_schedule = {"crontab": "* * * * 12"}
    with pytest.raises(WorkflowSyntaxError):
        build_celery_schedule("workflow_invalid_crontab", cron_schedule)


def test_build_celery_invalid_periodic_key():
    cron_schedule = {"non_valid_key": "* * * * *"}
    with pytest.raises(WorkflowSyntaxError):
        build_celery_schedule("workflow_invalid_key", cron_schedule)
