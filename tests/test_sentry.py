from director.extensions import DirectorSentry, cel_workflows, cel
from director.models.tasks import Task
from director.models.workflows import Workflow


def test_sentry_enrich_data(app, create_builder):
    _, wf = create_builder("example", "WORKFLOW", {})

    sentry = DirectorSentry()
    sentry.init_app(app)
    tags = sentry.enrich_tags(
        {"foo": "bar"}, wf.workflow_id, cel.tasks.get("TASK_EXAMPLE")
    )
    assert tags == {
        "foo": "bar",
        "celery_task_name": "TASK_EXAMPLE",
        "director_workflow_id": str(wf.workflow_id),
        "director_workflow_project": "example",
        "director_workflow_name": "example.WORKFLOW",
    }

    extra = sentry.enrich_extra(
        {"foo": "bar"}, [{"key": "value"}], {"payload": {"hello": "world"}}
    )
    assert extra == {
        "foo": "bar",
        "task-args": [{"key": "value"}],
        "workflow-payload": {"hello": "world"},
    }
