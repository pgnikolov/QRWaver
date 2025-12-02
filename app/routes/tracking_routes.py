"""Routes responsible for handling trackable short links and redirects.

The `/s/<slug>` endpoint records a scan and either redirects to the original
URL (for URL-type QRs) or serves a minimal landing page for non-URL content.
"""

from flask import Blueprint, request, redirect, jsonify, make_response
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
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

    # Build combined UTM map: incoming query params take precedence, then QR defaults
    allow = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}
    combined_utms = {k: (request.args.get(k) or getattr(qr, k) or None) for k in allow}

    # Treat None as trackable (backward compatibility for old rows without explicit True)
    if qr.is_trackable is not False:
        enriched = analytics.enrich_request(request)
        # If UTM fields are missing from the request, fill with QR defaults for logging
        for k, v in combined_utms.items():
            if not enriched.get(k):
                enriched[k] = v
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
        # Forward UTM params from the short link (or QR defaults) to the destination without
        # overwriting any existing UTM params already present on the target URL.
        class _ArgsProxy:
            def __init__(self, d):
                self._d = d
            def get(self, k, default=None):
                return self._d.get(k, default)
        target = _merge_utms_into_target(target, _ArgsProxy(combined_utms))
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
    """Minimal HTML escaping for inline landing content."""
    if text is None:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _merge_utms_into_target(target_url: str, incoming_args) -> str:
    """Merge allowed UTM parameters from the incoming request into target_url.

    - Only applies an allowlist of UTM keys.
    - Does not overwrite destination UTMs if already present.
    """
    allow = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}
    try:
        parsed = urlparse(target_url)
        dest_q = dict(parse_qsl(parsed.query, keep_blank_values=True))

        # Collect utms from incoming args (MultiDict-compatible)
        for k in allow:
            if k not in dest_q:
                v = incoming_args.get(k)
                if v:
                    dest_q[k] = v

        new_query = urlencode(dest_q, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    except Exception:
        # On any parsing error, return the original target URL unchanged
        return target_url
