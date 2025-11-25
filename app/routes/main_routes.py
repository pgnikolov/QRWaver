"""Primary site pages and template context processors.

Provides the public index/about pages, dashboard view, and context processors
to inject the current year and authentication state into all templates.
"""

from flask import Blueprint, render_template
from datetime import datetime, timezone

from flask_jwt_extended import jwt_required
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from app.routes.auth_routes import auth_bp

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


@main_bp.get("/dashboard")
@jwt_required(optional=True)
def dashboard_page():
    """Render the user dashboard page.

    Authentication is optional here so the page can render a friendly prompt
    for non-authenticated users while still functioning when logged in.
    """
    return render_template("dashboard.html")
