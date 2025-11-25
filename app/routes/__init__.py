from .main_routes import main_bp
from .api_routes import api_bp
from .qr_routes import qr_bp

def register_blueprints(app):
    """
    Registers all the blueprints to the provided Flask application.

    This function associates the application's routes with blueprints used
    in the project. Blueprints allow for modular development and better
    organization of the application's routes.

    :param app: The Flask application instance to which the blueprints
        will be registered. It is expected to be an instance of `flask.Flask`.
    :return: None
    """
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(qr_bp)

"""Route blueprints package for QRWaver.

This package contains Flask blueprints that implement the web UI pages and
the JSON/REST API endpoints used by the application.
"""
