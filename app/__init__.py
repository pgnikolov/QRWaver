# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from app.config.settings import Config, LOG_DIR, LOG_FILE
import logging

def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # -------------------------------
    # Logging – единствено място
    # -------------------------------
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(file_handler)

    # Console handler (important for render.com, docker & dev)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(console_handler)

    app.logger.info("🚀 QRWaver backend initialised")

    # -------------------------------
    # Register blueprints
    # -------------------------------
    from app.routes.main_routes import main_bp
    from app.routes.qr_routes import qr_bp
    from app.routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # -------------------------------
    # Global JSON error handler
    # -------------------------------
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

    # -------------------------------
    # Health & version
    # -------------------------------
    @app.route("/ping")
    def ping():
        return jsonify({"success": True, "status": "ok", "message": "QRWaver API online"})

    @app.route("/version")
    def version():
        return jsonify({
            "success": True,
            "version": "1.0.0",
            "build": "backend-stable"
        })

    return app
