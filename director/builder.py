from celery import chain, group
from celery.utils import uuid

from director.exceptions import WorkflowSyntaxError
from director.extensions import cel, cel_workflows
from director.models import StatusType
from director.models.tasks import Task
from director.models.workflows import Workflow
from director.tasks.workflows import start, end


class WorkflowBuilder(object):
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self._workflow = None

        self.queue = cel_workflows.get_queue(str(self.workflow))
        self.tasks = cel_workflows.get_tasks(str(self.workflow))
        self.canvas = []

        # Pointer to the previous task(s)
        self.previous = []

    @property
    def workflow(self):
        if not self._workflow:
            self._workflow = Workflow.query.filter_by(id=self.workflow_id).first()
        return self._workflow

    def new_task(self, task_name, single=True):
        task_id = uuid()

        # We create the Celery task specifying its UID
        signature = cel.tasks.get(task_name).subtask(
            kwargs={"workflow_id": self.workflow_id, "payload": self.workflow.payload},
            queue=self.queue,
            task_id=task_id,
        )

        # Director task has the same UID
        task = Task(
            id=task_id,
            key=task_name,
            previous=self.previous,
            workflow_id=self.workflow.id,
            status=StatusType.pending,
        )
        task.save()

        if single:
            self.previous = [signature.id]

        return signature

    def parse(self, tasks):
        canvas = []

        for task in tasks:
            if type(task) is str:
                signature = self.new_task(task)
                canvas.append(signature)
            elif type(task) is dict:
                name = list(task)[0]
                if "type" not in task[name] and task[name]["type"] != "group":
                    raise WorkflowSyntaxError()

                sub_canvas_tasks = [
                    self.new_task(t, single=False) for t in task[name]["tasks"]
                ]

                sub_canvas = group(*sub_canvas_tasks, task_id=uuid())
                canvas.append(sub_canvas)
                self.previous = [s.id for s in sub_canvas_tasks]
            else:
                raise WorkflowSyntaxError()

        return canvas

    def build(self):
        self.canvas = self.parse(self.tasks)
        self.canvas.insert(0, start.si(self.workflow.id).set(queue=self.queue))
        self.canvas.append(end.si(self.workflow.id).set(queue=self.queue))

    def run(self):
        if not self.canvas:
            self.build()

        canvas = chain(*self.canvas, task_id=uuid())

        try:
            return canvas.apply_async()
        except Exception as e:
            self.workflow.status = StatusType.error
            self.workflow.save()
            raise e
