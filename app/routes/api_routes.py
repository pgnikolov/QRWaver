from flask import Blueprint, jsonify, request
from app.services.qr_service import QRService
from app.services.rate_limiter import SimpleRateLimiter

api_bp = Blueprint("api", __name__)
_qr = QRService()
_limiter = SimpleRateLimiter(limit=3, window_seconds=300)  # 3 requests / 5 min per IP


@api_bp.route("/ping")
def ping():
    return jsonify({"status": "ok", "message": "QRWeaver API is running"})


@api_bp.route("/generate", methods=["POST"])
def generate_qr():
    # rate limit
    allowed, remaining = _limiter.allow(request)
    if not allowed:
        return jsonify({
            "success": False,
            "error": "Rate limit exceeded. Please try again later.",
            "limit": 3,
            "remaining": 0
        }), 429

    payload = request.get_json(silent=True, force=True) or {}

    qr_type = (payload.get("type") or "url").strip().lower()
    data = payload.get("data") or {}
    # For URL convenience: allow plain string
    if qr_type == "url" and isinstance(data, str):
        data = {"url": data}

    settings = payload.get("settings") or {}

    result = _qr.generate(qr_type, data, settings)

    # attach remaining quota meta
    result["rate_limit"] = {"limit": 3, "remaining": remaining}
    status = 200 if result.get("success") else 400
    return jsonify(result), status
# from flask import Blueprint, jsonify, request
# from app.services.qr_service import QRService
# from app.services.rate_limiter import SimpleRateLimiter
#
# api_bp = Blueprint("api", __name__)
# _qr = QRService()
# _limiter = SimpleRateLimiter(limit=3, window_seconds=300)  # 3 requests / 5 min per IP
#
#
# @api_bp.route("/ping")
# def ping():
#     return jsonify({"status": "ok", "message": "QRWeaver API is running"})
#
#
# @api_bp.route("/generate", methods=["POST"])
# def generate_qr():
#     # 🚫 TEMPORARILY DISABLE RATE LIMIT DURING TESTING
#     # allowed, remaining = _limiter.allow(request)
#     # if not allowed:
#     #     return jsonify({
#     #         "success": False,
#     #         "error": "Rate limit exceeded. Please try again later.",
#     #         "limit": 3,
#     #         "remaining": 0
#     #     }), 429
#
#     payload = request.get_json(silent=True, force=True) or {}
#
#     qr_type = (payload.get("type") or "url").strip().lower()
#     data = payload.get("data") or {}
#
#     # For URL convenience: allow plain string
#     if qr_type == "url" and isinstance(data, str):
#         data = {"url": data}
#
#     settings = payload.get("settings") or {}
#
#     result = _qr.generate(qr_type, data, settings)
#
#     # attach remaining quota meta
#     result["rate_limit"] = {"limit": 3, "remaining": 3}  # <- fake constant remaining quota
#     status = 200 if result.get("success") else 400
#     return jsonify(result), status
