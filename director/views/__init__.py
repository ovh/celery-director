from uuid import UUID

from flask import Blueprint, abort, render_template


view_bp = Blueprint("views", __name__, url_prefix="/")


@view_bp.route("/")
def home():
    return render_template("index.html")


@view_bp.route("/<id>")
def get_workflow(id):
    try:
        _ = UUID(id)
    except ValueError:
        abort(404)
    return render_template("index.html")


@view_bp.app_template_filter("status")
def status(code):
    return {
        "pending": "secondary",
        "progress": "warning",
        "success": "success",
        "error": "danger",
        "canceled": "dark",
    }[code]
