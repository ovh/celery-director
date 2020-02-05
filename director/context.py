import os

import click

from director import create_app


class DirectorContext(click.Context):
    def __init__(self):
        self.app = create_app()
        self.app.app_context().push()


context = DirectorContext
pass_ctx = click.make_pass_decorator(context, ensure=True)
