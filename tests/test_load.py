import pytest

from director.extensions import CeleryWorkflow


@pytest.mark.parametrize("fmt", [("yml"), ("json")])
def test_load_workflow_formats(app, fmt):
    app.config["WORKFLOW_FORMAT"] = fmt
    name = f"example.{fmt.upper()}_WORKFLOW"

    cel_workflows = CeleryWorkflow()
    cel_workflows.init_app(app)
    cel_workflows.get_by_name(name)
