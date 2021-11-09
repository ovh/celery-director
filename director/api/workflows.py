from datetime import datetime, timedelta
from distutils.util import strtobool

import pytz
from flask import abort, jsonify, request
from flask import current_app as app

from director.api import api_bp, validate
from director.auth import auth
from director.builder import WorkflowBuilder
from director.exceptions import WorkflowNotFound
from director.extensions import cel_workflows, schema
from director.models.workflows import Workflow
from director.utils import build_celery_schedule


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
    # Convert with_payload arg to boolean, if we encounter an error,
    # ignore and set with_payload to its default value (True)
    # We don't do request.args.get with type=bool because it doesn't seem to work as expected because
    # this most likely casts the string as bool which is not the proper string to bool conversion we need
    try:
        with_payload = strtobool(
            request.args.get("with_payload", type=str, default="True")
        )
    except ValueError:
        with_payload = True
    per_page = request.args.get(
        "per_page", type=int, default=app.config["WORKFLOWS_PER_PAGE"]
    )
    workflows = Workflow.query.order_by(Workflow.created_at.desc()).paginate(
        page, per_page
    )
    return jsonify([w.to_dict(with_payload=with_payload) for w in workflows.items])


@api_bp.route("/workflows/<workflow_id>")
@auth.login_required
def get_workflow(workflow_id):
    workflow = _get_workflow(workflow_id)
    tasks = [t.to_dict() for t in workflow.tasks]

    resp = workflow.to_dict()
    resp.update({"tasks": tasks})
    return jsonify(resp)


@api_bp.route("/list/workflows")
@auth.login_required
def get_definition():
    tz = pytz.utc
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get(
        "per_page", type=int, default=app.config["WORKFLOWS_PER_PAGE"]
    )
    data = [
        {"fullname": k, "project": k.split(".")[0], "name": k.split(".")[1], **v}
        for k, v in sorted(cel_workflows.workflows.items(), key=lambda item: item[0])
    ]
    data = data[per_page * (page - 1) : per_page * page - 1]
    for item in data:
        if item.get("periodic"):
            _, schedule = build_celery_schedule("name", item["periodic"])
            last_workflow = (
                Workflow.query.filter_by(name=item["name"], project=item["project"])
                .order_by(Workflow.created_at.desc())
                .first()
            )
            now = tz.localize(datetime.now())
            last_run = tz.localize(last_workflow.created_at) if last_workflow else now
            if isinstance(schedule, float):
                delta = timedelta(seconds=schedule)
                next_run = last_run + delta if last_run + delta > now else now + delta
            else:
                delta = schedule.remaining_estimate(last_run)
                next_run = (
                    last_run + delta
                    if last_run + delta > now
                    else now + schedule.remaining_estimate(now)
                )
            item["next_run"] = next_run
    return jsonify(data)
