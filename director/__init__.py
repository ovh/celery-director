import importlib
import os
import pkgutil
from functools import partial
from pathlib import Path

from flask import Flask, Blueprint, jsonify, request, render_template
from flask_json_schema import JsonValidationError
from werkzeug.exceptions import InternalServerError, HTTPException

from director.api import api_bp
from director.extensions import cel, cel_workflows, db, schema, sentry, migrate
from director.settings import Config, UserConfig
from director.tasks.base import BaseTask
from director.views import view_bp

with open(Path(__file__).parent.resolve() / "VERSION", encoding="utf-8") as version:
    __version__ = version.readline().rstrip()


# Proxify the task method
task = partial(cel.task, base=BaseTask)


# Provide the user config
config = UserConfig()


# Custom Flask class
class DirectorFlask(Flask):
    static_folder = "static"
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(variable_start_string="%%", variable_end_string="%%",))


# Create the application using a factory
def create_app(
    home_path=os.getenv("DIRECTOR_HOME"), config_path=os.getenv("DIRECTOR_CONFIG")
):
    app = DirectorFlask(__name__)
    c = Config(home_path, config_path)
    app.config.from_object(c)

    # Init User's config
    config.init()

    # Init Blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(view_bp)
    # Init the blueprint for the User's static assets
    app.register_blueprint(
        Blueprint(
            "user",
            __name__,
            static_url_path="/static/user",
            static_folder=str(Path(app.config["STATIC_FOLDER"])),
        )
    )

    # Error handler
    app.register_error_handler(HTTPException, lambda e: http_exception_handler(e))

    # Init extensions
    db.init_app(app)
    db.app = app

    migrate.init_app(
        app=app, db=db, directory=str(Path(__file__).resolve().parent / "migrations"),
    )
    schema.init_app(app)
    cel.init_app(app)
    cel_workflows.init_app(app)
    sentry.init_app(app)

    # Register the periodic tasks for Celery Beat
    for workflow, conf in cel_workflows.workflows.items():
        if "periodic" in conf:
            payload = conf.get("periodic").get("payload", {})
            schedule = conf.get("periodic").get("schedule")

            cel.conf.beat_schedule.update(
                {
                    f"periodic-{workflow}-{schedule}s": {
                        "task": "director.tasks.periodic.execute",
                        "schedule": schedule,
                        "args": (workflow, payload,),
                    }
                }
            )

    return app


def http_exception_handler(error):
    if request.path.startswith("/api"):
        return jsonify(error=str(error.description)), error.code

    return render_template("error.html", error=error), error.code


# Import director's submodules
def import_submodules(package, modules_to_import):
    """
    Import all submodules of a module, recursively, including subpackages.
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}

    for loader, full_name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        name = full_name.split(".")[-1]
        if not name.startswith("_") and not name.startswith("tests"):

            if any(x in package.__name__ for x in modules_to_import) or any(
                x in name for x in modules_to_import
            ):
                results[full_name] = importlib.import_module(full_name)
                if is_pkg:
                    results.update(import_submodules(full_name, modules_to_import))
    return results


import_submodules(__name__, ("api", "models", "tasks", "views"))
