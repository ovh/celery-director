from pathlib import Path

import click


ENV_TEMPLATE = """# Auto-generated, please adjust
# Director API endpoint
DIRECTOR_API_URL="http://127.0.0.1:8000/api"

# Director relational database
DIRECTOR_DATABASE_URI="sqlite:///{{director_home}}/director.db"

# Celery
DIRECTOR_BROKER_URI="redis://127.0.0.1:6379"
"""


WORKFLOWS_YML_TEMPLATE = """---
# Simple ETL example
#
# +-----------+      +-------------+      +--------+
# |  EXTRACT  +----->+  TRANSFORM  +----->+  LOAD  |
# +-----------+      +-------------+      +--------+
#
ovh.SIMPLE_ETL:
  tasks:
    - EXTRACT
    - TRANSFORM
    - LOAD
"""


ETL_PY_TEMPLATE = """from director import task


@task(name="EXTRACT")
def extract(*args, **kwargs):
    print("Extracting data")


@task(name="TRANSFORM")
def transform(*args, **kwargs):
    print("Transforming data")


@task(name="LOAD")
def load(*args, **kwargs):
    print("Loading data")
"""


@click.command()
@click.argument("path")
def init(path):
    """
    Create a new project
    """
    user_project_path = Path(path).resolve()
    user_project_path.mkdir(parents=True, exist_ok=True)
    (user_project_path / "tasks").mkdir(exist_ok=True)

    with open(user_project_path / ".env", "w", encoding="utf-8") as f:
        f.write(ENV_TEMPLATE.replace("{{director_home}}", str(user_project_path)))

    with open(user_project_path / "workflows.yml", "w", encoding="utf-8") as f:
        f.write(WORKFLOWS_YML_TEMPLATE)

    with open(user_project_path / "tasks" / "etl.py", "w", encoding="utf-8") as f:
        f.write(ETL_PY_TEMPLATE)

    click.echo(f"[*] Project created in {user_project_path}")
    click.echo("You can now export the DIRECTOR_HOME environment variable")
