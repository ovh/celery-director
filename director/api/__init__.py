from flask import jsonify, Blueprint
from flask_json_schema import JsonValidationError
from jsonschema.exceptions import ValidationError, SchemaError
from jsonschema.validators import validator_for


# Main application
api_bp = Blueprint("api", __name__, url_prefix="/api")


# Validate a payload according to a given schema
def validate(payload, schema):
    validator_cls = validator_for(schema)
    validator = validator_cls(schema=schema)
    errors = list(validator.iter_errors(payload))
    if errors:
        raise JsonValidationError("Payload is not valid", errors)


@api_bp.errorhandler(JsonValidationError)
def schema_exception_handler(e):
    return (
        jsonify(
            {
                "error": e.message,
                "errors": [validation_err.message for validation_err in e.errors],
            }
        ),
        400,
    )


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": error.description}), 404


@api_bp.route("/ping")
def ping():
    return jsonify({"message": "pong"})
