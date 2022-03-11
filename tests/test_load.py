import pytest

from director.extensions import CeleryWorkflow


@pytest.mark.parametrize("fmt", [("yml"), ("json")])
def test_load_workflow_formats(app, fmt):
    app.config["WORKFLOW_FORMAT"] = fmt
    name = f"example.{fmt.upper()}_WORKFLOW"

    cel_workflows = CeleryWorkflow()
    cel_workflows.init_app(app)
    cel_workflows.get_by_name(name)


def test_load_workflow_folder(app):
    app.config["WORKFLOW_FOLDER"] = "folder/sub_folder"
    name_template = "example.FOLDER_{}"
    cel_workflows = CeleryWorkflow()
    cel_workflows.init_app(app)

    assert len(cel_workflows.workflows) == 4
    for i in range(1, 5):
        name = name_template.format(i)
        cel_workflows.get_by_name(name)


def test_load_workflow_folder_fails_for_duplicates(app):
    app.config["WORKFLOW_FOLDER"] = "folder"
    cel_workflows = CeleryWorkflow()
    expected_message = "Duplicate workflows loaded"

    with pytest.raises(ValueError) as error:
        cel_workflows.init_app(app)
    assert str(error.value) == expected_message
