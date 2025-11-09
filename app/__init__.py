from flask import Flask
from flask_cors import CORS
from app.config.settings import Config



def create_app():
    """Initialize Flask app with all blueprints and extensions."""
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # --- Register blueprints ---
    from app.routes.main_routes import main_bp
    from app.routes.qr_routes import qr_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(qr_bp, url_prefix="/qr")
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
