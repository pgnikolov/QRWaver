# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from app.config.settings import Config, LOG_DIR, LOG_FILE
from app.extensions.extensions import init_extensions, db
import logging
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Init DB + JWT + CORS
    init_extensions(app)
    CORS(app, supports_credentials=True)

    # -------------------------------
    # Logging – единствено място
    # -------------------------------
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Ensure log dir exists
    os.makedirs(LOG_DIR, exist_ok=True)

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
    from app.routes.auth_routes import auth_bp
    from app.routes.qr_api_routes import qr_api
    from app.routes.google_auth import google_auth
    from app.routes.api_routes import api_bp
    from app.routes.qr_v1_routes import qr_v1_bp
    from app.routes.tracking_routes import tracking_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(qr_api)
    app.register_blueprint(google_auth)
    # Versioned API blueprints
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(qr_v1_bp)
    app.register_blueprint(tracking_bp)

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

    # -------------------------------
    # DEV: Auto-create tables
    # -------------------------------
    from app.models.user import User
    from app.models.qr_code import QRCode
    from app.models.qr_scan import QRScan

    with app.app_context():
        from app.models.user import User
        from app.models.qr_code import QRCode
        from app.models.qr_scan import QRScan

        try:
            db.create_all()
            app.logger.info("✅ DB tables ensured via db.create_all()")
        except Exception as e:
            app.logger.error(f"❌ DB init error: {e}")

    return app
