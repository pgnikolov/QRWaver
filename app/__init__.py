from flask import Flask, jsonify
from flask_cors import CORS
from app.config.settings import Config
import logging
import os


def create_app():
    """
    Creates and configures the Flask application instance.

    This function sets up the application with necessary configurations, logging,
    blueprints, and error handlers. Additionally, it defines routes for health
    and version checks.

    :returns: Configured Flask application instance.
    :rtype: Flask
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # --- Logging setup ---
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "api.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    # --- Register blueprints ---
    from app.routes.main_routes import main_bp
    from app.routes.qr_routes import qr_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(qr_bp, url_prefix="/qr")
    app.register_blueprint(api_bp, url_prefix="/api")

    # --- Global JSON error handler ---
    @app.errorhandler(Exception)
    def handle_exception(e):
        code = getattr(e, "code", 500)
        message = str(e)
        app.logger.exception(f"Unhandled exception: {message}")
        return jsonify({
            "success": False,
            "error": message,
            "code": code
        }), code

    # --- Health & version routes ---
    @app.route("/ping")
    def ping():
        return jsonify({"success": True, "status": "ok", "message": "QRWeaver API online"})

    @app.route("/version")
    def version():
        return jsonify({
            "success": True,
            "version": "1.0.0",
            "build": "backend-stable"
        })

    return app
