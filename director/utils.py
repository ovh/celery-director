from flask_json_schema import JsonValidationError
from jsonschema.validators import validator_for
from celery.schedules import crontab

from director.exceptions import WorkflowSyntaxError


def validate(payload, schema):
    """Validate a payload according to a given schema"""
    validator_cls = validator_for(schema)
    validator = validator_cls(schema=schema)
    errors = list(validator.iter_errors(payload))
    if errors:
        raise JsonValidationError("Payload is not valid", errors)


def format_schema_errors(e):
    """Format FlaskJsonSchema validation errors"""
    return {
        "error": e.message,
        "errors": [validation_err.message for validation_err in e.errors],
    }


def build_celery_schedule(workflow_name, data):
    """ A celery schedule can accept seconds or crontab """
    try:
        schedule = float(data)
    except ValueError:
        try:
            m, h, dw, dm, my = data.split(" ")

            schedule = crontab(
                minute=m,
                hour=h,
                day_of_week=dw,
                day_of_month=dm,
                month_of_year=my,
            )
        except Exception as e:
            raise WorkflowSyntaxError(workflow_name)

    return schedule
