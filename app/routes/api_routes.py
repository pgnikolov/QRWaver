from flask import Blueprint, jsonify, request
from app.services.qr_service import QRService
from app.services.rate_limiter import SimpleRateLimiter
import logging

api_bp = Blueprint("api", __name__)
_qr = QRService()
#_limiter = SimpleRateLimiter(limit=3, window_seconds=300)  # 3 requests / 5 min per IP
_limiter = SimpleRateLimiter(limit=9999, window_seconds=10) # for testing
logger = logging.getLogger(__name__)


@api_bp.route("/generate", methods=["POST"])
def generate_qr():
    try:
        # Rate limit check
        allowed, remaining = _limiter.allow(request)
        if not allowed:
            logger.warning(f"Rate limit exceeded for {request.remote_addr}")
            return jsonify({
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "limit": 3,
                "remaining": 0
            }), 429

        payload = request.get_json(silent=True, force=True) or {}

        qr_type = (payload.get("type") or "url").strip().lower()
        data = payload.get("data") or {}
        settings = payload.get("settings") or {}

        logger.info(f"Generating QR ({qr_type}) for {request.remote_addr}")

        result = _qr.generate(qr_type, data, settings)
        result["rate_limit"] = {"limit": 3, "remaining": remaining}
        status = 200 if result.get("success") else 400

        return jsonify(result), status

    except Exception as e:
        logger.exception(f"Error during QR generation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/ping")
def ping():
    return jsonify({"success": True, "status": "ok", "message": "QRWeaver API online"})


@api_bp.route("/version")
def version():
    return jsonify({
        "success": True,
        "version": "1.0.0",
        "build": "backend-stable"
    })
