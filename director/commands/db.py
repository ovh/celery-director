from pathlib import Path

import click
from alembic import command
from alembic.config import Config

from director.context import pass_ctx


@click.command()
@pass_ctx
def upgradedb(ctx):
    """Upgrade the database schema"""
    path = Path(__file__).resolve().parent.parent
    conf = Config(str(path / "migrations" / "alembic.ini"))
    conf.set_main_option("script_location", str(path / "migrations"))
    command.upgrade(conf, "heads")
