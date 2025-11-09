from flask import Blueprint, jsonify, request
from app.services.qr_service import QRService
from app.services.rate_limiter import SimpleRateLimiter
import logging

api_bp = Blueprint("api", __name__)

# QR generator core
_qr = QRService()

# Rate limiter
_limiter = SimpleRateLimiter(limit=9999, window_seconds=10)  # TEMP for development

logger = logging.getLogger(__name__)


@api_bp.route("/generate", methods=["POST"])
def generate_qr():
    try:
        # Rate limit check
        allowed, remaining = _limiter.allow(request)
        if not allowed:
            return jsonify({
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "limit": 3,
                "remaining": 0
            }), 429

        # Read JSON
        payload = request.get_json(silent=True, force=True) or {}
        print("\n Incoming QR API payload:", payload, "\n")

        # Extract QR type
        qr_type = (payload.get("type") or "url").strip().lower()

        # Extract data (string or dict)
        data = payload.get("data")
        if not isinstance(data, (dict, str)):
            data = str(data or "")

        # Extract settings (colors, size, frame_type, etc.)
        settings = payload.get("settings") or {}

        # Generate the QR
        result = _qr.generate(qr_type, data, settings)
        result["rate_limit"] = {"limit": 3, "remaining": remaining}

        status = 200 if result.get("success") else 400
        return jsonify(result), status

    except Exception as e:
        logger.exception(f"Error during QR generation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/ping")
def ping():
    return jsonify({"success": True, "status": "ok"})


@api_bp.route("/version")
def version():
    return jsonify({
        "success": True,
        "version": "1.0.0",
        "build": "backend-clean"
    })
