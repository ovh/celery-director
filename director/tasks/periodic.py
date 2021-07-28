import logging

from flask import jsonify

from director.builder import WorkflowBuilder
from director.extensions import cel, db
from director.models import StatusType
from director.models.workflows import Workflow


logger = logging.getLogger()


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


@cel.task()
def cleanup(retentions):
    count = 0
    for workflow, retention in retentions.items():
        project, name = workflow.split(".")
        logger.info(f"Cleaning {workflow} (retention of {retention}).")
        rows_of_workflow = (
            Workflow.query.filter_by(
                project=project, name=name, status=StatusType.success
            )
            .order_by(Workflow.created_at.desc())
            .offset(retention)
            .all()
        )

        ids = [row.id for row in rows_of_workflow]
        if not ids:
            logger.info(f"No need to clean {workflow}.")
            continue

        Workflow.query.filter(Workflow.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        count += len(ids)
        logger.info(f"{len(ids)} workflows deleted.")
    return count
