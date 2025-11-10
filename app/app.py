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

    # Регистрираме всички blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
