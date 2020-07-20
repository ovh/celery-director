import click

from director import __version__
from director.commands.assets import dlassets
from director.commands.celery import celery
from director.commands.db import db
from director.commands.init import init
from director.commands.user import user
from director.commands.webserver import webserver
from director.commands.workflows import workflow


@click.version_option(version=__version__)
@click.group()
def cli():
    """Celery Director - Command Line Interface"""
    pass


cli.add_command(webserver)
cli.add_command(celery)
cli.add_command(workflow)
cli.add_command(db)
cli.add_command(user)
cli.add_command(dlassets)
cli.add_command(init)
