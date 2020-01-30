import os
import click


@click.command(context_settings=dict(ignore_unknown_options=True))
@click.option("--dev", "dev_mode", default=False, is_flag=True, type=bool)
@click.argument("web_args", nargs=-1, type=click.UNPROCESSED)
def webserver(dev_mode, web_args):
    """Start the webserver instance"""
    if dev_mode:
        os.environ["FLASK_APP"] = f"director._auto:app"
        os.environ["FLASK_DEBUG"] = "1"
        args = [
            "flask",
            "run",
            "--port",
            "8000",
        ]
        args += list(web_args)
        os.execvpe(args[0], args, os.environ)
    else:
        args = [
            "gunicorn",
        ]
        args += list(web_args)
        args.append("director._auto:app")
        os.execvp(args[0], args)
