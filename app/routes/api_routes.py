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
    """
    Handles the QR code generation API endpoint.

    This function processes incoming POST requests, extracts relevant data and settings from
    the JSON payload, and generates a QR code based on the supplied parameters. It includes rate
    limiting to prevent abuse of the API. Upon successful QR code generation, the result is
    returned in JSON format along with rate limit details. If any exceptions occur, it handles
    them gracefully and returns a JSON-formatted error response.

    :param api_bp.route: The route and HTTP method for the endpoint.
    :type api_bp.route: str
    :return: A JSON response containing the generated QR code result, rate limit details, or
             an error message if the generation fails.
    :rtype: flask.Response
    :raises: Returns HTTP 400 for bad requests, HTTP 429 for rate limit violations,
             and HTTP 500 for unexpected server errors.
    """
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
    """
    Handles the 'ping' endpoint in the API which is used to check the status
    and availability of the service. The endpoint returns a simple JSON
    response indicating the service is operational.

    :return: A JSON response with keys 'success' indicating operation
             success and 'status' showing 'ok'.
    :rtype: flask.Response
    """
    return jsonify({"success": True, "status": "ok"})


@api_bp.route("/version")
def version():
    """
    Returns information about the current API version.

    Provides details including the version number of the API and the build
    identifier. This endpoint helps clients understand the current version
    and build of the backend system they are interacting with.

    :returns: A JSON response containing the API version and build
              information.
    :rtype: flask.Response
    """
    return jsonify({
        "success": True,
        "version": "1.0.0",
        "build": "backend-clean"
    })
