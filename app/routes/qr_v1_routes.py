from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.qr_service import QRService
from app.extensions.extensions import db
from app.models.qr_code import QRCode
from app.services.rate_limiter import SimpleRateLimiter
from app.services.analytics_service import AnalyticsService
from sqlalchemy import func
from app.config.settings import PUBLIC_BASE_URL


qr_v1_bp = Blueprint("qr_v1", __name__, url_prefix="/api/v1/qr")
qr_service = QRService()
_preview_limiter = SimpleRateLimiter(limit=120, window_seconds=60)
analytics = AnalyticsService()


@qr_v1_bp.route("/preview", methods=["POST"])
def preview_qr_v1():
    """
    Lightweight preview generator (no auth, no persistence).
    Returns a data URI (SVG) suitable for instant client-side preview.
    Rate limited per IP.
    """
    allowed, remaining = _preview_limiter.allow(request)
    if not allowed:
        response = jsonify({
            "success": False,
            "error": "Rate limit exceeded. Please try again later.",
            "limit": _preview_limiter.limit,
            "remaining": 0,
            "window": _preview_limiter.window,
        })
        response.status_code = 429
        response.headers["X-RateLimit-Limit"] = str(_preview_limiter.limit)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["X-RateLimit-Window"] = str(_preview_limiter.window)
        return response

    payload = request.get_json(silent=True) or {}
    qr_type = (payload.get("type") or "text").strip().lower()
    data = payload.get("data")
    settings = payload.get("settings") or {}

    if data in (None, ""):
        return jsonify({"success": False, "error": "Missing data"}), 400

    try:
        text = qr_service.build_payload(qr_type, data)
        size = int(settings.get("size") or 512)
        svg_bytes = qr_service._generate_svg_bytes(text, size=size)  # noqa: protected-access used intentionally
        data_uri = "data:image/svg+xml;base64," + __import__("base64").b64encode(svg_bytes).decode("ascii")

        response = jsonify({
            "success": True,
            "image": data_uri,
            "mime": "image/svg+xml",
            "width": size,
            "height": size,
            "rate_limit": {
                "limit": _preview_limiter.limit,
                "remaining": remaining,
                "window": _preview_limiter.window,
            },
        })
        response.headers["X-RateLimit-Limit"] = str(_preview_limiter.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(_preview_limiter.window)
        return response
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@qr_v1_bp.route("/create", methods=["POST"])
@jwt_required()
def create_qr_v1():
    """
    Create (persist) a QR code for the authenticated user.

    Expected JSON body:
    {
      "type": "url|text|wifi|email|phone|vcard|youtube|social|...",
      "data": <string|object>,
      "settings": { "format": "svg|png|jpg", "size": 512, ... },
      "frame": "none|frame_whole|frame_phone|frame_bag|frame_2parts"  // optional, currently ignored server-side
    }

    Notes:
    - Real-time preview should be client-side; this endpoint persists once on Save.
    - For now all QR types are allowed. A soft limit of max 5 saved QRs per user is enforced.
    """
    payload = request.get_json(silent=True) or {}
    user_id = get_jwt_identity()

    qr_type = (payload.get("type") or "text").strip().lower()
    data = payload.get("data")
    settings = payload.get("settings") or {}

    if data in (None, ""):
        return jsonify({"success": False, "error": "Missing data"}), 400

    # Enforce a simple saved QR limit for now (max 5 per user)
    count = QRCode.query.filter_by(user_id=user_id).count()
    if count >= 5:
        return jsonify({
            "success": False,
            "error": "Free plan limit reached (5 QRs). You can remove older QRs to create new ones."
        }), 403

    try:
        # Build QR payload text from the given type+data
        original_payload_text = qr_service.build_payload(qr_type, data)

        # Extract rendering format/size
        fmt = (settings.get("format") or "svg").lower()
        size = int(settings.get("size") or 512)

        # Generate short slug for tracking (analytics) first so we can
        # encode the trackable URL inside the QR image itself.
        slug = analytics.generate_slug()

        # Build short URL using a public base if configured; fall back to request.host
        def _base_url() -> str:
            """
            Decide which base URL to embed inside the QR image.

            Rationale:
            - In development we must use the current request host (localhost) so
              that the generated short URL points back to the dev server where
              the slug is stored (SQLite dev DB). If we were to always use the
              PUBLIC_BASE_URL from the .env, scans would hit the production
              domain which doesn't have the dev slug, resulting in
              {"success": False, "error": "Not found"}.
            - In production, prefer PUBLIC_BASE_URL when provided; otherwise
              fall back to the request host.
            """
            from flask import current_app as app

            # Prefer dynamic host in non-production environments
            env = (app.config.get("ENV") or "").lower()
            debug = bool(app.config.get("DEBUG"))
            if env != "production" or debug:
                return request.host_url.rstrip("/")

            # Production: use configured public base if available
            base = (PUBLIC_BASE_URL or "").strip()
            if base:
                if not (base.startswith("http://") or base.startswith("https://")):
                    base = "https://" + base
                return base.rstrip("/")

            # Fallback
            return request.host_url.rstrip("/")

        base = _base_url()
        short_url = f"{base}/s/{slug}"

        # If trackable, we want the QR code image to contain the short URL
        # so that every real-world scan hits our /s/<slug> endpoint and is counted.
        qr_content = short_url

        # Render + upload the QR that contains the short URL
        result = qr_service.create_and_upload_qr(
            user_id=user_id,
            payload=qr_content,
            fmt=fmt,
            size=size,
        )

        # Persist DB record: store the ORIGINAL payload for reference/redirects
        record = QRCode(
            user_id=user_id,
            qr_type=qr_type,
            payload=original_payload_text,
            file_path=result["url"],
            slug=slug,
            is_trackable=True,
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            "success": True,
            "url": result["url"],
            "record_id": record.id,
            "short_url": short_url,
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@qr_v1_bp.route("", methods=["GET"])
@jwt_required()
def list_qr_v1():
    user_id = get_jwt_identity()
    items = (
        QRCode.query
        .filter_by(user_id=user_id)
        .order_by(QRCode.created_at.desc())
        .all()
    )

    resp = []
    # helper to compute public base URL consistently with create endpoint
    def _base_url() -> str:
        """
        Same base URL decision logic as in create_qr_v1(). See rationale there.
        """
        from flask import current_app as app

        env = (app.config.get("ENV") or "").lower()
        debug = bool(app.config.get("DEBUG"))
        if env != "production" or debug:
            return request.host_url.rstrip("/")

        base = (PUBLIC_BASE_URL or "").strip()
        if base:
            if not (base.startswith("http://") or base.startswith("https://")):
                base = "https://" + base
            return base.rstrip("/")
        return request.host_url.rstrip("/")
    base = _base_url()
    for qr in items:
        # Build short URL if slug is present
        short_url = None
        if qr.slug:
            short_url = f"{base}/s/{qr.slug}"
        resp.append({
            "id": qr.id,
            "qr_type": qr.qr_type,
            "payload": qr.payload,
            "url": qr.file_path,  # we store the full URL here in v1
            "scan_count": qr.scan_count,
            "created_at": qr.created_at.isoformat() if qr.created_at else None,
            "slug": qr.slug,
            "short_url": short_url,
            "is_trackable": bool(qr.is_trackable),
        })

    return jsonify({"success": True, "items": resp}), 200


@qr_v1_bp.route("/<int:qr_id>/stats", methods=["GET"])
@jwt_required()
def qr_stats_v1(qr_id: int):
    """
    Basic stats endpoint: returns totals, daily series, and simple breakdowns.
    Query params: from, to (ISO8601), group=day (default)
    """
    user_id = get_jwt_identity()
    qr = QRCode.query.filter_by(id=qr_id, user_id=user_id).first()
    if not qr:
        return jsonify({"success": False, "error": "Not found"}), 404

    # Parse query params
    start = request.args.get("from")
    end = request.args.get("to")
    group = request.args.get("group", "day")

    out = analytics.get_stats(qr.id, start, end, group)
    return jsonify({"success": True, **out}), 200


@qr_v1_bp.route("/<int:qr_id>", methods=["DELETE"])
@jwt_required()
def delete_qr_v1(qr_id: int):
    """
    Delete a QR owned by the authenticated user.

    Important: DB-only delete. We DO NOT delete the underlying asset from R2.
    This invalidates the short link and removes the item from dashboard and stats.
    """
    user_id = get_jwt_identity()
    qr = QRCode.query.filter_by(id=qr_id, user_id=user_id).first()
    if not qr:
        return jsonify({"success": False, "error": "Not found"}), 404

    try:
        db.session.delete(qr)
        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
