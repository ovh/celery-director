from flask import Blueprint, render_template


view_bp = Blueprint("views", __name__, url_prefix="/")


@view_bp.route("/")
def home():
    return render_template("index.html")


@view_bp.route("/workflows/<id>", methods=["GET"])
def displayWorkflow(id):
    return render_template("index.html")


@view_bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@view_bp.app_template_filter("status")
def status(code):
    return {
        "pending": "secondary",
        "progress": "warning",
        "success": "success",
        "error": "danger",
        "canceled": "dark",
    }[code]
