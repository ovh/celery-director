import imp
from pathlib import Path

import yaml
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_json_schema import JsonSchema, JsonValidationError
from flask_migrate import Migrate
from pluginbase import PluginBase

from director.exceptions import WorkflowNotFound


class CeleryWorkflow:
    def __init__(self):
        self.app = None
        self.workflows = None

    def init_app(self, app):
        self.app = app
        self.path = Path(self.app.config["DIRECTOR_HOME"]).resolve() / "workflows.yml"
        with open(self.path) as f:
            self.workflows = yaml.load(f, Loader=yaml.SafeLoader)
        self.import_user_tasks()

    def get_by_name(self, name):
        workflow = self.workflows.get(name)
        if not workflow:
            raise WorkflowNotFound(f"Workflow {name} not found")
        return workflow

    def get_tasks(self, name):
        return self.get_by_name(name)["tasks"]

    def import_user_tasks(self):
        self.plugin_base = PluginBase(package="director.foobar")

        folder = Path(self.app.config["DIRECTOR_HOME"]).resolve()
        self.plugin_source = self.plugin_base.make_plugin_source(
            searchpath=[str(folder)]
        )

        tasks = Path(folder / "tasks").glob("**/*.py")
        with self.plugin_source:
            for task in tasks:
                if task.stem == "__init__":
                    continue

                name = str(task.relative_to(folder))[:-3].replace("/", ".")
                __import__(
                    self.plugin_source.base.package + "." + name,
                    globals(),
                    {},
                    ["__name__"],
                )


# Celery Extension
class FlaskCelery(Celery):
    def __init__(self, *args, **kwargs):
        kwargs["include"] = ["director.tasks"]
        super(FlaskCelery, self).__init__(*args, **kwargs)

        if "app" in kwargs:
            self.init_app(kwargs["app"])

    def init_app(self, app):
        self.app = app
        self.conf.update(app.config.get("CELERY_CONF", {}))


# List of extensions
db = SQLAlchemy()
migrate = Migrate()
schema = JsonSchema()
cel = FlaskCelery("director")
cel_workflows = CeleryWorkflow()
