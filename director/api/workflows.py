from flask import current_app as app
from flask import jsonify, request

from director.api import api_bp
from director.builder import WorkflowBuilder
from director.exceptions import WorkflowNotFound
from director.extensions import cel_workflows, schema
from director.models.workflows import Workflow


@api_bp.route("/workflows", methods=["POST"])
@schema.validate(
    {
        "required": ["project", "name", "payload"],
        "additionalProperties": False,
        "properties": {
            "project": {"type": "string"},
            "name": {"type": "string"},
            "payload": {"type": "object"},
        },
    }
)
def create_workflow():
    data = request.get_json()
    project = data["project"]
    name = data["name"]
    fullname = f"{project}.{name}"

    # Check if the workflow exists
    try:
        cel_workflows.get_by_name(fullname)
    except WorkflowNotFound:
        return jsonify({"error": f"Workflow {fullname} not found"}), 404

    # Create the workflow in DB
    obj = Workflow(project=project, name=name, payload=data["payload"])
    obj.save()

    # Build the workflow and execute it
    data = obj.to_dict()
    workflow = WorkflowBuilder(obj.id)
    workflow.run()

    app.logger.info(f"Workflow ready : {workflow.canvas}")
    return jsonify(data), 201


@api_bp.route("/workflows")
def list_workflows():
    workflows = Workflow.query.all()
    return jsonify([w.to_dict() for w in workflows])


@api_bp.route("/workflows/<workflow_id>")
def get_workflow(workflow_id):
    workflow = Workflow.query.filter_by(id=workflow_id).first()
    if not workflow:
        return jsonify({"error": f"Workflow {workflow_id} not found"}), 404

    tasks = [t.to_dict() for t in workflow.tasks]
    resp = workflow.to_dict()
    resp.update({"tasks": tasks})

    return jsonify(resp)
