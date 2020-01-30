from director.builder import WorkflowBuilder
from director.extensions import cel
from director.models.workflows import Workflow


@cel.task()
def execute(workflow, payload):
    project, name = workflow.split(".")
    c_obj = Workflow(project=project, name=name, payload=payload, periodic=True)
    c_obj.save()

    # Build the workflow and execute it
    workflow = WorkflowBuilder(c_obj.id)
    workflow.run()

    return c_obj.to_dict()
