from flask import Blueprint, jsonify, request
from app.services.qr_service import QRService
from app.services.rate_limiter import SimpleRateLimiter
import logging

api_bp = Blueprint("api", __name__)

# QR generator core
_qr = QRService()

# Rate limiter – 60 заявки / 60 секунди на IP (може да пипаме после)
_limiter = SimpleRateLimiter(limit=60, window_seconds=60)

logger = logging.getLogger(__name__)


@api_bp.route("/generate", methods=["POST"])
def generate_qr():
    """
    QR generation endpoint.

    - Rate limiting per IP
    - Delegates QR building to QRService
    - Returns JSON with image data URI + basic metadata
    - Връща реални rate-limit стойности в JSON и в HTTP headers
    """
    try:
        # ----------------- Rate limit check -----------------
        allowed, remaining = _limiter.allow(request)
        if not allowed:
            response = jsonify({
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "limit": _limiter.limit,
                "remaining": 0,
                "window": _limiter.window,
            })
            response.status_code = 429
            # Стандартни rate-limit headers
            response.headers["X-RateLimit-Limit"] = str(_limiter.limit)
            response.headers["X-RateLimit-Remaining"] = "0"
            response.headers["X-RateLimit-Window"] = str(_limiter.window)
            return response

        # ----------------- Read JSON payload -----------------
        payload = request.get_json(silent=True, force=True) or {}
        logger.debug("Incoming QR API payload: %s", payload)

        # Extract QR type
        qr_type = (payload.get("type") or "url").strip().lower()

        # Extract data (string or dict)
        data = payload.get("data")
        if not isinstance(data, (dict, str)):
            data = str(data or "")

        # Extract settings (color, size, format, etc.)
        settings = payload.get("settings") or {}

        # ----------------- Generate the QR -----------------
        result = _qr.generate(qr_type, data, settings)

        # Добавяме rate-limit метаданни към JSON
        result["rate_limit"] = {
            "limit": _limiter.limit,
            "remaining": remaining,
            "window": _limiter.window,
        }

        status = 200 if result.get("success") else 400

        response = jsonify(result)
        response.status_code = status

        # И в HTTP headers – полезно за SaaS / dashboard / clients
        response.headers["X-RateLimit-Limit"] = str(_limiter.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(_limiter.window)

        return response

    except Exception as e:
        logger.exception(f"Error during QR generation: {e}")
        # Не изнасяме raw exception към клиента
        response = jsonify({"success": False, "error": "Internal server error"})
        response.status_code = 500
        return response


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
