from flask import current_app as app
from flask import abort, jsonify, request
from jsonschema.exceptions import ValidationError, SchemaError

from director.api import api_bp, validate
from director.auth import auth
from director.builder import WorkflowBuilder
from director.exceptions import WorkflowNotFound
from director.extensions import cel_workflows, schema
from director.models.workflows import Workflow


def _get_workflow(workflow_id):
    workflow = Workflow.query.filter_by(id=workflow_id).first()
    if not workflow:
        abort(404, f"Workflow {workflow_id} not found")
    return workflow


def _execute_workflow(project, name, payload={}):
    fullname = f"{project}.{name}"

    # Check if the workflow exists
    try:
        wf = cel_workflows.get_by_name(fullname)
        if "schema" in wf:
            validate(payload, wf["schema"])
    except WorkflowNotFound:
        abort(404, f"Workflow {fullname} not found")

    # Create the workflow in DB
    obj = Workflow(project=project, name=name, payload=payload)
    obj.save()

    # Build the workflow and execute it
    data = obj.to_dict()
    workflow = WorkflowBuilder(obj.id)
    workflow.run()

    app.logger.info(f"Workflow sent : {workflow.canvas}")
    return obj.to_dict(), workflow


@api_bp.route("/workflows", methods=["POST"])
@auth.login_required
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
    project, name, payload = (
        request.get_json()["project"],
        request.get_json()["name"],
        request.get_json()["payload"],
    )
    data, _ = _execute_workflow(project, name, payload)
    return jsonify(data), 201


@api_bp.route("/workflows/<workflow_id>/relaunch", methods=["POST"])
@auth.login_required
def relaunch_workflow(workflow_id):
    obj = _get_workflow(workflow_id)
    data, _ = _execute_workflow(obj.project, obj.name, obj.payload)
    return jsonify(data), 201


@api_bp.route("/workflows")
@auth.login_required
def list_workflows():
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get(
        "per_page", type=int, default=app.config["WORKFLOWS_PER_PAGE"]
    )
    workflows = Workflow.query.order_by(Workflow.created_at.desc()).paginate(
        page, per_page
    )
    return jsonify([w.to_dict() for w in workflows.items])


@api_bp.route("/workflows/<workflow_id>")
@auth.login_required
def get_workflow(workflow_id):
    workflow = _get_workflow(workflow_id)
    tasks = [t.to_dict() for t in workflow.tasks]

    resp = workflow.to_dict()
    resp.update({"tasks": tasks})
    return jsonify(resp)
