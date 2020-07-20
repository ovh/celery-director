from flask import current_app as app
from flask import jsonify, abort
from flask_httpauth import HTTPBasicAuth

from director.models.users import User

from werkzeug.security import check_password_hash

ANONYMOUS_USERNAME = "anonymous"

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    # no need to check if auth is disabled
    if not app.config.get("AUTH_ENABLED"):
        return ANONYMOUS_USERNAME

    # return false if auth is enabled and no username is set
    if not username:
        return

    user = User.query.filter_by(username=username).first()
    if not user:
        return

    # auth is enabled, needs to check the credz
    if check_password_hash(user.password, password):
        return username


@auth.error_handler
def unauthorized():
    response = jsonify(
        {
            "status": 401,
            "error": "unauthorized",
            "message": "Please authenticate to access this API.",
        }
    )
    response.status_code = 401
    return response
