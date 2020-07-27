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

    c_obj_dict = c_obj.to_dict()

    # Force commit before ending the function to ensure the ongoing transaction
    # does not end up in a "idle in transaction" state on PostgreSQL
    c_obj.commit()

    return c_obj_dict
