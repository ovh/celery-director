import os

import click


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("db_args", nargs=-1, type=click.UNPROCESSED)
def db(db_args):
    """Manage the database"""
    os.environ["FLASK_APP"] = "director._auto:app"
    args = ["flask", "db"] + list(db_args)
    os.execvpe(args[0], args, os.environ)
