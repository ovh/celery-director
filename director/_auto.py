# initialize a working context
import os

from director import create_app
from director.extensions import cel

app = create_app(os.getenv("DIRECTOR_HOME"))
