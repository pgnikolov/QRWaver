"""Primary site pages and template context processors.

Provides the public index/about pages, dashboard view, and context processors
to inject the current year and authentication state into all templates.
"""

from flask import Blueprint, render_template
from datetime import datetime, timezone

from flask_jwt_extended import jwt_required
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.routes.auth_routes import auth_bp
from flask import current_app, request, Response, url_for
from app.config.settings import PUBLIC_BASE_URL

main_bp = Blueprint("main", __name__)


@main_bp.app_context_processor
def inject_now():
    """
    Provides a context processor to inject the current year into templates.

    This function is registered to the Flask application and executes within
    the application context. It retrieves the current year in UTC time and
    makes it available in templates under the key ``current_year``.

    :return: A dictionary with the current year as an integer under the key
        ``current_year``.
    :rtype: dict
    """
    return {'current_year': datetime.now(timezone.utc).year}


@main_bp.app_context_processor
def inject_auth_state():
    """
    Injects simple authentication state flags into all templates.

    Sets:
    - ``is_authenticated``: True if a valid JWT cookie is present, else False.
    - ``current_user_id``: The user id from JWT when available, else None.
    """
    try:
        # Will not raise if no token; makes the check lightweight for public pages
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        return {
            'is_authenticated': bool(identity),
            'current_user_id': identity if identity else None,
        }
    except Exception:
        return {
            'is_authenticated': False,
            'current_user_id': None,
        }

@main_bp.route("/")
def index():
    """
    Handles the root route of the application, rendering the homepage.

    The function serves the main entry point for the frontend user interface,
    by rendering the HTML template for the index page. It uses the Flask
    `render_template` function to dynamically generate the content of the
    homepage.

    :return: A rendered HTML template of the application's homepage, with the
        title 'QRWeaver – Create Beautiful QR Codes'.
    :rtype: Response
    """
    return render_template("index.html", title="QRWeaver – Create Beautiful QR Codes")

@main_bp.route("/about")
def about():
    """
    Handles the rendering of the 'About' page for the QRWeaver application.

    This function is mapped to the `/about` route of the application and is
    responsible for returning the 'About' page template along with its specified title.

    :return: The rendered HTML content of the 'About' page template.
    :rtype: werkzeug.wrappers.response.Response
    """
    return render_template("about.html", title="About QRWeaver")


@main_bp.route("/why")
def why_page():
    """Render the marketing page explaining "Why QRWaver?".

    The page highlights core value propositions, how it works, use cases,
    privacy/security notes, and an FAQ, with a clear call to action.
    """
    return render_template("why.html", title="Why QRWaver?")


@main_bp.route("/docs")
def docs_page():
    """Render the documentation page with quickstart and API reference."""
    return render_template("docs.html", title="QRWaver Docs")


@main_bp.get("/dashboard")
@jwt_required(optional=True)
def dashboard_page():
    """Render the user dashboard page.

    Authentication is optional here so the page can render a friendly prompt
    for non-authenticated users while still functioning when logged in.
    """
    return render_template("dashboard.html")


## (removed earlier duplicate sitemap route)


# ---------------------------------
# SEO: robots.txt and sitemap.xml
# ---------------------------------

@main_bp.get("/robots.txt")
def robots_txt():
    """Serve robots.txt to guide crawlers.

    Allows public marketing/docs pages and disallows private areas and APIs.
    Adjust as needed when adding more public pages.
    """
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /dashboard",
        "Disallow: /auth/",
        "Disallow: /api/",
        # Short redirect endpoints are not useful to index; avoid bloat
        "Disallow: /s/",
        "Sitemap: {}".format(_public_base_url().rstrip("/") + "/sitemap.xml"),
    ]
    content = "\n".join(lines) + "\n"
    return Response(content, mimetype="text/plain; charset=utf-8")


def _public_base_url() -> str:
    """Compute public base URL using config PUBLIC_BASE_URL or request host.

    Mirrors logic from API routes: prefer config in production, otherwise host.
    """
    from app.config.settings import PUBLIC_BASE_URL

    env = (current_app.config.get("ENV") or "").lower()
    debug = bool(current_app.config.get("DEBUG"))
    if env != "production" or debug:
        return request.host_url.rstrip("/")

    base = (PUBLIC_BASE_URL or "").strip()
    if base and not (base.startswith("http://") or base.startswith("https://")):
        base = "https://" + base
    return (base or request.host_url).rstrip("/")


@main_bp.get("/sitemap.xml")
def sitemap_xml():
    """Dynamic sitemap for core public pages rendered via template.

    Lists the primary marketing/pages and editor entry points. Excludes
    authenticated and API endpoints. The template is simple XML suitable
    for search engines.
    """
    base = _public_base_url()
    pages = [
        ("main.index", {}),
        ("main.why_page", {}),
        ("main.docs_page", {}),
        ("main.about", {}),
        # Editor landing pages (static marketing endpoints under /qr/<type>)
        ("qr.qr_editor", {"qr_type": "url"}),
        ("qr.qr_editor", {"qr_type": "wifi"}),
        ("qr.qr_editor", {"qr_type": "vcard"}),
        ("qr.qr_editor", {"qr_type": "text"}),
        ("qr.qr_editor", {"qr_type": "email"}),
        ("qr.qr_editor", {"qr_type": "phone"}),
        ("qr.qr_editor", {"qr_type": "youtube"}),
        ("qr.qr_editor", {"qr_type": "facebook"}),
        ("qr.qr_editor", {"qr_type": "instagram"}),
        ("qr.qr_editor", {"qr_type": "linkedin"}),
        ("qr.qr_editor", {"qr_type": "tiktok"}),
        ("qr.qr_editor", {"qr_type": "twitter"}),
    ]

    now_iso = datetime.now(timezone.utc).date().isoformat()
    entries = []
    for endpoint, params in pages:
        try:
            path = url_for(endpoint, **params)
        except Exception:
            continue
        entries.append({
            "loc": f"{base}{path}",
            "lastmod": now_iso,
            "changefreq": "weekly",
            "priority": "0.8",
        })

    xml = render_template("sitemap.xml", entries=entries)
    return Response(xml, mimetype="application/xml; charset=utf-8")
