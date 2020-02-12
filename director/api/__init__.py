from flask import jsonify, Blueprint


# Main application
api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": error.description}), 404


@api_bp.route("/ping")
def ping():
    return jsonify({"message": "pong"})
