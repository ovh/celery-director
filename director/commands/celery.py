import os
import click

from urllib.parse import urlparse

from director.context import pass_ctx


@click.group()
def celery():
    """Celery commands"""


@celery.command(name="beat", context_settings=dict(ignore_unknown_options=True))
@click.option("--dev", "dev_mode", default=False, is_flag=True, type=bool)
@click.argument("beat_args", nargs=-1, type=click.UNPROCESSED)
def beat(dev_mode, beat_args):
    """Start the beat instance"""
    args = [
        "celery",
        "beat",
        "-A",
        "director._auto:cel",
    ]
    if dev_mode:
        args += [
            "--loglevel",
            "INFO",
        ]
    args += list(beat_args)
    os.execvp(args[0], args)


@celery.command("worker", context_settings=dict(ignore_unknown_options=True))
@click.option("--dev", "dev_mode", default=False, is_flag=True, type=bool)
@click.argument("worker_args", nargs=-1, type=click.UNPROCESSED)
def worker(dev_mode, worker_args):
    """Start a Celery worker instance"""
    args = [
        "celery",
        "worker",
        "-A",
        "director._auto:cel",
    ]
    if dev_mode:
        args += [
            "--loglevel",
            "INFO",
        ]
    args += list(worker_args)
    os.execvp(args[0], args)


@celery.command(name="flower", context_settings=dict(ignore_unknown_options=True))
@click.argument("flower_args", nargs=-1, type=click.UNPROCESSED)
@pass_ctx
def flower(ctx, flower_args):
    """Start the flower instance"""
    broker = ctx.app.config["CELERY_CONF"]["broker_url"]
    args = ["flower", "-b", broker] + list(flower_args)
    os.execvp(args[0], args)
