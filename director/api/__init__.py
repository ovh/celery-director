from flask import jsonify, Blueprint
from flask_json_schema import JsonValidationError

from director.utils import validate, format_schema_errors
from director.auth import auth

# Main application
api_bp = Blueprint("api", __name__, url_prefix="/api")


# Check login for each api request
@api_bp.before_request
@auth.login_required
def before_request():
    pass


@api_bp.errorhandler(JsonValidationError)
def schema_exception_handler(e):
    return jsonify(format_schema_errors(e)), 400


@api_bp.route("/ping")
def ping():
    return jsonify({"message": "pong"})


@api_bp.route("/check_credentials")
def check_credentials():
    return jsonify({}), 204
