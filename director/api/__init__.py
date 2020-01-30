from flask import jsonify, Blueprint


# Main application
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/ping")
def ping():
    return jsonify({"message": "pong"})
