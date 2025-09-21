from flask import Blueprint, jsonify, request, current_app
from ..utils import require_admin, send_password_reset_email
import logging


admin_bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)


@admin_bp.get('/api/admin/status/email')
def admin_status_email():
    if not require_admin():
        return jsonify({"error": "forbidden"}), 403
    cfg = current_app.config
    return jsonify({
        "resend_available": bool(cfg.get('RESEND_AVAILABLE')),
        "has_api_key": bool(cfg.get('RESEND_API_KEY')),
        "email_from": cfg.get('EMAIL_FROM'),
        "frontend_base_url": cfg.get('FRONTEND_BASE_URL'),
        "environment": cfg.get('ENVIRONMENT', cfg.get('ENV')),
    })


@admin_bp.post('/api/admin/test-email')
def admin_test_email():
    if not require_admin():
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(silent=True) or {}
    to = (data.get('to') or '').strip()
    if not to:
        return jsonify({"error": "missing 'to'"}), 400

    # Use the same helper as password reset to ensure identical code path
    # Token not relevant; just demonstrate a link placeholder
    token = 'admin-test-token'
    try:
        ok = send_password_reset_email(to, token)
        return jsonify({"success": ok})
    except Exception as e:
        logger.exception("[admin-test-email] error: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500

