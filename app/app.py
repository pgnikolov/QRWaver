"""Flask application factory for legacy/simple app entry point.

This module defines a lightweight `create_app` used by some scripts and
historic entry points. The primary, more feature‑complete factory lives in
`app.__init__.py`. Both factories are safe to use, but the one in
`app.__init__` includes logging, error handlers, and additional blueprints.
"""

from flask import Flask
from app.routes.main_routes import main_bp
from app.routes.qr_routes import qr_bp
from app.routes.api_routes import api_bp
from app.config.settings import Config


def create_app():
    """
    Creates and configures the Flask application instance.

    This function initializes the Flask application with its configuration
    and registers all required blueprints to provide modular organization
    and routing for the application.

    :returns: A Flask application instance configured and ready for use.
    :rtype: Flask
    """
    app = Flask(__name__)

    app.config.from_object(Config)

    # Register all blueprints for the simple app setup
    app.register_blueprint(main_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
