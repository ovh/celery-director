from celery import chain, group
from celery.utils import uuid
from celery.utils.log import get_task_logger
from director.extensions import cel
from director.models import StatusType
from director.models.workflows import Workflow
from director.tasks.base import BaseTask

logger = get_task_logger(__name__)


@cel.task(name="celery.ping")
def ping():
    # type: () -> str
    """Simple task that just returns 'pong'."""
    return "pong"


@cel.task()
def start(workflow_id):
    logger.info(f"Opening the workflow {workflow_id}")
    workflow = Workflow.query.filter_by(id=workflow_id).first()
    workflow.status = StatusType.progress
    workflow.save()


@cel.task()
def end(workflow_id):
    logger.info(f"Closing the workflow {workflow_id}")
    workflow = Workflow.query.filter_by(id=workflow_id).first()

    if workflow.status != StatusType.error:
        workflow.status = StatusType.success
        workflow.save()


@cel.task()
def sub_flows(result, subflows, **kwargs):

    if not subflows:
        return result

    from director.builder import WorkflowBuilder

    for sub in subflows:
        project, name = sub.split(".")
        obj = Workflow(project=project, name=name, payload=result)
        obj.save()
        builder = WorkflowBuilder(obj.id)
        builder.build()
        builder.run()
