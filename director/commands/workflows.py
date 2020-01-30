import click
import json
from json.decoder import JSONDecodeError
from terminaltables import AsciiTable

from director.builder import WorkflowBuilder
from director.context import pass_ctx
from director.exceptions import WorkflowNotFound
from director.extensions import cel_workflows
from director.models.workflows import Workflow


@click.group()
def workflow():
    """Manage the workflows"""


@workflow.command(name="list")
@pass_ctx
def list_workflow(ctx):
    """List the workflows"""
    workflows = {
        k: v
        for k, v in sorted(cel_workflows.workflows.items(), key=lambda item: item[0])
    }

    data = [[f"Workflows ({len(workflows)})", "Periodic", "Tasks"]]

    # Add a row for each workflow
    for name, conf in workflows.items():

        # Periodic info
        periodic = conf.get("periodic", {}).get("schedule", "--")

        # Wrap the tasks list
        tasks_str = ""
        for task in conf["tasks"]:
            tasks_str += f"{task}\n"

        # Just remove the last newline
        if tasks_str:
            tasks_str = tasks_str[:-1]

        data.append([name, periodic, tasks_str])

    table = AsciiTable(data)
    table.inner_row_border = True
    table.justify_columns[1] = "center"
    click.echo(table.table)


@workflow.command(name="show")
@click.argument("name")
@pass_ctx
def show_workflow(ctx, name):
    """Display details of a workflow"""
    data = []
    try:
        workflow = cel_workflows.get_by_name(name)
    except WorkflowNotFound as e:
        click.echo(f"Error: {e}")
        return

    # Construct the table
    data.append(["Name", name])

    # Wrap the tasks list
    tasks_str = ""
    for task in workflow["tasks"]:
        tasks_str += f"{task}\n"

    # Just remove the last newline
    if tasks_str:
        tasks_str = tasks_str[:-1]
    data.append(["Tasks", tasks_str])

    # Handle periodic information
    periodic = workflow.get("periodic", {}).get("schedule", "--")
    data.append(["Periodic", periodic])

    payload = workflow.get("periodic", {}).get("payload", {})
    data.append(["Payload", payload])

    table = AsciiTable(data)
    table.inner_heading_row_border = False
    table.inner_row_border = True
    click.echo(table.table)


@workflow.command(name="run")
@click.argument("fullname")
@click.argument("payload", required=False, default="{}")
@pass_ctx
def run_workflow(ctx, fullname, payload):
    """Execute a workflow"""
    try:
        cel_workflows.get_by_name(fullname)
        payload = json.loads(payload)
    except WorkflowNotFound as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
    except JSONDecodeError as e:
        click.echo(f"Error parsing the JSON payload : {e}")
        raise click.Abort()

    # Create the workflow object
    project, name = fullname.split(".")
    obj = Workflow(project=project, name=name, payload=payload)
    obj.save()

    # Build the canvas and execute it
    _workflow = WorkflowBuilder(obj.id)
    _workflow.run()
