import click

from director.commands.assets import dlassets
from director.commands.celery import celery
from director.commands.db import db
from director.commands.init import init
from director.commands.webserver import webserver
from director.commands.workflows import workflow


@click.group()
def cli():
    """Celery Director - Command Line Interface"""
    pass


cli.add_command(webserver)
cli.add_command(celery)
cli.add_command(workflow)
cli.add_command(db)
cli.add_command(dlassets)
cli.add_command(init)
