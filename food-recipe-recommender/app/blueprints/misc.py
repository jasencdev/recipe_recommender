from flask import Blueprint, jsonify, Response

misc_bp = Blueprint('misc', __name__)


@misc_bp.get('/api/health')
def health() -> Response:
    return jsonify({"status": "healthy"})

