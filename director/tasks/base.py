from celery import Task as _Task
from celery.signals import after_task_publish, task_prerun, task_postrun
from celery.utils.log import get_task_logger

from director.extensions import cel, db
from director.models import StatusType
from director.models.workflows import Workflow
from director.models.tasks import Task


logger = get_task_logger(__name__)


@task_prerun.connect
def director_prerun(task_id, task, *args, **kwargs):
    if task.name.startswith("director.tasks"):
        return

    with cel.app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        task.status = StatusType.progress
        task.save()


@task_postrun.connect
def close_session(*args, **kwargs):
    # Flask SQLAlchemy will automatically create new sessions for you from
    # a scoped session factory, given that we are maintaining the same app
    # context, this ensures tasks have a fresh session (e.g. session errors
    # won't propagate across tasks)
    db.session.remove()


class BaseTask(_Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        task = Task.query.filter_by(id=task_id).first()
        task.status = StatusType.error
        task.result = {"exception": str(exc), "traceback": einfo.traceback}
        task.workflow.status = StatusType.error
        task.save()

        logger.info(f"Task {task_id} is now in error")
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        task = Task.query.filter_by(id=task_id).first()
        task.status = StatusType.success
        task.result = retval
        task.save()

        logger.info(f"Task {task_id} is now in success")
        super(BaseTask, self).on_success(retval, task_id, args, kwargs)
