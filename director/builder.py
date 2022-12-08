from celery import chain, group
from celery.utils import uuid

from director.exceptions import WorkflowSyntaxError
from director.extensions import cel, cel_workflows
from director.models import StatusType
from director.models.tasks import Task
from director.models.workflows import Workflow
from director.tasks.workflows import start, end, failure_hooks_launcher


class WorkflowBuilder(object):
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self._workflow = None

        self.queue = cel_workflows.get_queue(str(self.workflow))
        self.custom_queues = {}

        self.tasks = cel_workflows.get_tasks(str(self.workflow))
        self.canvas = []

        self.failure_hook = cel_workflows.get_failure_hook_task(str(self.workflow))
        self.failure_hook_canvas = []

        self.success_hook = cel_workflows.get_success_hook_task(str(self.workflow))
        self.success_hook_canvas = []

        # Pointer to the previous task(s)
        self.previous = []

    @property
    def workflow(self):
        if not self._workflow:
            self._workflow = Workflow.query.filter_by(id=self.workflow_id).first()
        return self._workflow

    def new_task(self, task_name, is_hook, single=True):
        task_id = uuid()

        queue = self.custom_queues.get(task_name, self.queue)

        # We create the Celery task specifying its UID
        signature = cel.tasks.get(task_name).subtask(
            kwargs={"workflow_id": self.workflow_id, "payload": self.workflow.payload},
            queue=queue,
            task_id=task_id,
        )

        # Director task has the same UID
        task = Task(
            id=task_id,
            key=task_name,
            previous=self.previous,
            workflow_id=self.workflow.id,
            status=StatusType.pending,
            is_hook=is_hook,
        )
        task.save()

        if single:
            self.previous = [signature.id]

        return signature

    def parse_queues(self):
        if type(self.queue) is dict:
            self.custom_queues = self.queue.get("customs", {})
            self.queue = self.queue.get("default", "celery")
        if type(self.queue) is not str or type(self.custom_queues) is not dict:
            raise WorkflowSyntaxError()

    def parse(self, tasks, is_hook=False):
        canvas = []

        for task in tasks:
            if type(task) is str:
                signature = self.new_task(task, is_hook)
                canvas.append(signature)
            elif type(task) is dict:
                name = list(task)[0]
                if "type" not in task[name] and task[name]["type"] != "group":
                    raise WorkflowSyntaxError()

                sub_canvas_tasks = [
                    self.new_task(t, is_hook, single=False) for t in task[name]["tasks"]
                ]

                sub_canvas = group(*sub_canvas_tasks, task_id=uuid())
                canvas.append(sub_canvas)
                self.previous = [s.id for s in sub_canvas_tasks]
            else:
                raise WorkflowSyntaxError()

        return canvas

    def build(self):
        self.parse_queues()
        self.canvas = self.parse(self.tasks)
        self.canvas.insert(0, start.si(self.workflow.id).set(queue=self.queue))
        self.canvas.append(end.si(self.workflow.id).set(queue=self.queue))

    def build_hooks(self):
        initial_previous = self.previous

        if self.failure_hook and not self.failure_hook_canvas:
            self.previous = None
            self.failure_hook_canvas = [
                failure_hooks_launcher.si(
                    self.workflow.id,
                    self.queue,
                    [self.failure_hook],
                    self.workflow.payload,
                ).set(queue=self.queue),
            ]

        if self.success_hook and not self.success_hook_canvas:
            self.previous = None
            self.success_hook_canvas = [self.parse([self.success_hook], True)[0]]

        self.previous = initial_previous

    def run(self):
        if not self.canvas:
            self.build()

        canvas = chain(*self.canvas, task_id=uuid())

        self.build_hooks()

        try:
            return canvas.apply_async(
                link=self.success_hook_canvas,
                link_error=self.failure_hook_canvas,
            )

        except Exception as e:
            self.workflow.status = StatusType.error
            self.workflow.save()
            raise e

    def cancel(self):
        status_to_cancel = set([StatusType.pending, StatusType.progress])
        for task in self.workflow.tasks:
            if task.status in status_to_cancel:
                cel.control.revoke(task.id, terminate=True)
                task.status = StatusType.canceled
                task.save()
        self.workflow.status = StatusType.canceled
        self.workflow.save()
