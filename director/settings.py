import os
from pathlib import Path

from environs import Env


HIDDEN_CONFIG = [
    "DIRECTOR_ENABLE_DARK_THEME",
    "DIRECTOR_ENABLE_HISTORY_MODE",
    "DIRECTOR_API_URL",
    "DIRECTOR_FLOWER_URL",
    "DIRECTOR_DATABASE_URI",
    "DIRECTOR_DATABASE_POOL_RECYCLE",
    "DIRECTOR_BROKER_URI",
    "DIRECTOR_RESULT_BACKEND_URI",
    "DIRECTOR_SENTRY_DSN",
]


class Config(object):
    def __init__(self, home_path=None, config_path=None):
        if not home_path or not Path(home_path).resolve().exists():
            raise ValueError("environment variable DIRECTOR_HOME is not set correctly")
        self.DIRECTOR_HOME = env_path = str(home_path)

        if config_path:
            if not Path(config_path).resolve().exists():
                raise ValueError(
                    "environment variable DIRECTOR_CONFIG is not set correctly"
                )
            env_path = config_path

        env = Env()
        env.read_env(env_path)

        self.ENABLE_DARK_THEME = env.bool("DIRECTOR_ENABLE_DARK_THEME", False)
        self.ENABLE_HISTORY_MODE = env.bool("DIRECTOR_ENABLE_HISTORY_MODE", False)
        self.ENABLE_CDN = env.bool("DIRECTOR_ENABLE_CDN", True)
        self.STATIC_FOLDER = env.str(
            "DIRECTOR_STATIC_FOLDER", str(Path(self.DIRECTOR_HOME).resolve() / "static")
        )
        self.API_URL = env.str("DIRECTOR_API_URL", "http://127.0.0.1:8000/api")
        self.FLOWER_URL = env.str("DIRECTOR_FLOWER_URL", "http://127.0.0.1:5555")
        self.WORKFLOWS_PER_PAGE = env.int("DIRECTOR_WORKFLOWS_PER_PAGE", 1000)

        # Authentication
        self.AUTH_ENABLED = env.bool("DIRECTOR_AUTH_ENABLED", False)

        # SQLAlchemy configuration
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_DATABASE_URI = env.str("DIRECTOR_DATABASE_URI", "")
        self.SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_recycle": env.int("DIRECTOR_DATABASE_POOL_RECYCLE", -1),
        }

        # Celery configuration
        self.CELERY_CONF = {
            "task_always_eager": False,
            "broker_url": env.str("DIRECTOR_BROKER_URI", "redis://localhost:6379/0"),
            "result_backend": env.str(
                "DIRECTOR_RESULT_BACKEND_URI", "redis://localhost:6379/1"
            ),
            "broker_transport_options": {"master_name": "director"},
        }

        # Sentry configuration
        self.SENTRY_DSN = env.str("DIRECTOR_SENTRY_DSN", "")


class UserConfig(dict):
    """Handle the user configuration"""

    def init(self):
        envs = {
            k.split("DIRECTOR_")[1]: v
            for k, v in os.environ.items()
            if k.startswith("DIRECTOR_") and k not in HIDDEN_CONFIG
        }
        super().__init__(**envs)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as e:
            raise AttributeError(f"Config '{e.args[0]}' not defined")
