from types import MappingProxyType
from uuid import uuid4

import celery

from director.exceptions import WorkflowSyntaxError
from director.extensions import cel, cel_workflows
from director.models import StatusType
from director.models.tasks import Task
from director.models.workflows import Workflow
from director.tasks.workflows import start, end


class WorkflowBuilder(object):
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self._blueprint = cel_workflows.get_by_name(str(self.workflow))
        self.default_queue = self.blueprint.get("queue", "celery")
        self.complex = self.blueprint.get("complex")
        self.canvas = []
        self.previous = []

    @property
    def blueprint(self):
        if not getattr(self, "_blueprint_proxy", None):
            self._blueprint_proxy = MappingProxyType(self._blueprint)
        return self._blueprint_proxy

    @property
    def workflow(self):
        if not getattr(self, "_workflow", None):
            self._workflow = Workflow.query.filter_by(id=self.workflow_id).first()
        return self._workflow

    def new_task(self, name, single=True, options=None, kwargs=None, **params):
        task_id = str(uuid4())
        options, kwargs = options or {}, kwargs or {}
        options = {**self.blueprint.get("options", {}), **options}
        options["queue"] = params.get("queue", self.default_queue)
        kwargs.update(workflow_id=self.workflow_id, payload=self.workflow.payload)

        # Create a Celery task specifying its UUID
        task = cel.tasks.get(name)
        signature = task.subtask(task_id=task_id, kwargs=kwargs, **options)

        # Create a Director task with the same UUID
        task = Task(
            id=task_id,
            key=name,
            queue=options["queue"],
            previous=self.previous,
            workflow_id=self.workflow_id,
            status=StatusType.pending,
        ).save()

        if single:
            self.previous = [signature.id]

        return signature

    def new_group(self, item):
        group_tasks = [self.new_task(**t, single=False) for t in item["tasks"]]
        self.previous = [s.id for s in group_tasks]
        return celery.group(*group_tasks, task_id=str(uuid4()))

    def parse_simple_item(self, item):
        to_obj = lambda x: {"name": x, "type": "task"}
        if type(item) is str:
            return to_obj(item)
        if type(item) is dict:
            name = next(iter(item))
            item = {"name": name, **item[name]}
            if item.get("tasks"):
                item["tasks"] = [to_obj(x) for x in item["tasks"]]
            return item

    def parse(self):
        canvas = []
        for item in self.blueprint["tasks"]:
            if not self.complex:
                item = self.parse_simple_item(item)
            if item["type"] == "task":
                signature = self.new_task(**item)
                canvas.append(signature)
                continue
            if item["type"] == "group":
                sub_canvas = self.new_group(item)
                canvas.append(sub_canvas)
                continue
            raise WorkflowSyntaxError
        return canvas

    def build(self):
        start_task = start.si(self.workflow_id).set(queue=self.default_queue)
        end_task = end.si(self.workflow_id).set(queue=self.default_queue)
        self.canvas = self.parse()
        self.canvas.insert(0, start_task)
        self.canvas.append(end_task)

    def run(self):
        if not self.canvas:
            self.build()

        canvas = celery.chain(*self.canvas, task_id=str(uuid4()))

        try:
            return canvas.apply_async()
        except Exception as e:
            self.workflow.status = StatusType.error
            self.workflow.save()
            raise e
