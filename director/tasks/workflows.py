from celery.utils.log import get_task_logger

from director.extensions import cel
from director.tasks.base import BaseTask
from director.models import StatusType
from director.models.workflows import Workflow


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
