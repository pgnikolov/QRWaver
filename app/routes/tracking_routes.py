from flask import Blueprint, request, redirect, jsonify, make_response
from app.models.qr_code import QRCode
from app.services.analytics_service import AnalyticsService


tracking_bp = Blueprint("tracking", __name__)
analytics = AnalyticsService()


@tracking_bp.route("/s/<slug>", methods=["GET"])
def short_redirect(slug: str):
    """
    Trackable short URL endpoint.
    - Lookup QR by slug
    - Log scan with basic enrichment
    - Redirect to destination if URL type, otherwise render simple landing content
    """
    if not slug:
        return jsonify({"success": False, "error": "Missing slug"}), 400

    qr = QRCode.query.filter_by(slug=slug).first()
    if not qr:
        return jsonify({"success": False, "error": "Not found"}), 404

    # Treat None as trackable (backward compatibility for old rows without explicit True)
    if qr.is_trackable is not False:
        enriched = analytics.enrich_request(request)
        try:
            analytics.log_scan(qr, enriched)
        except Exception as e:
            # Do not block redirect on analytics failure, but log for diagnostics
            try:
                from flask import current_app as app
                app.logger.error(f"analytics.log_scan failed for QR id={qr.id}, slug={slug}: {e}")
            except Exception:
                pass

    # Redirect only for URL payloads; otherwise render minimal landing
    if (qr.qr_type or "").lower() == "url":
        target = qr.payload
        # Basic safety: ensure it starts with http(s)
        if not (target.startswith("http://") or target.startswith("https://")):
            target = "https://" + target
        return redirect(target, code=302)

    # Simple inline landing page for non-URL payloads
    html = f"""
    <!doctype html>
    <html lang=\"en\">
      <head>
        <meta charset=\"utf-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
        <title>QR Content</title>
        <style>
          body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }}
          .card {{ max-width: 720px; margin: auto; padding: 1.5rem; border: 1px solid #e5e7eb; border-radius: 12px; }}
          pre {{ white-space: pre-wrap; word-wrap: break-word; }}
          .meta {{ color: #6b7280; font-size: 0.9rem; margin-bottom: .5rem; }}
        </style>
      </head>
      <body>
        <div class=\"card\">
          <div class=\"meta\">QR type: {qr.qr_type}</div>
          <pre>{_escape_html(qr.payload)}</pre>
        </div>
      </body>
    </html>
    """
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


def _escape_html(text: str) -> str:
    if text is None:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
