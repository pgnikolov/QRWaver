"""Application factory and core backend setup for QRWaver.

This module provides the primary Flask application factory used by the
project, including configuration selection, extension initialization,
blueprint registration, logging, error handlers, and a few utility
endpoints such as health and version.
"""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException, NotFound
from flask_cors import CORS
from app.config.settings import Config, LOG_DIR, LOG_FILE, DevelopmentConfig, ProductionConfig
from app.extensions.extensions import init_extensions, db
import logging
import os
from app.config.settings import R2_PUBLIC_BASE_URL


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Select config based on environment
    config_name = os.getenv("APP_SETTINGS")
    if not config_name:
        env = (os.getenv("FLASK_ENV") or os.getenv("ENV") or "").lower()
        if env == "production":
            config = ProductionConfig
        elif env == "development" or os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            config = DevelopmentConfig
        else:
            config = Config
    else:
        # Support simple names
        mapping = {
            "Config": Config,
            "DevelopmentConfig": DevelopmentConfig,
            "ProductionConfig": ProductionConfig,
            "dev": DevelopmentConfig,
            "prod": ProductionConfig,
        }
        config = mapping.get(config_name, Config)

    app.config.from_object(config)

    # Init DB + JWT + CORS
    init_extensions(app)
    CORS(app, supports_credentials=True)

    # -------------------------------
    # Logging — single, centralized configuration
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

    # Console handler (useful for Render, Docker, and local development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(console_handler)

    app.logger.info("🚀 QRWaver backend initialised")
    try:
        app.logger.info(f"✅ Using config: {config.__name__}")
    except Exception:
        pass

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
    # Unversioned legacy API under /api (matches tests expecting /api/generate)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(qr_v1_bp)
    app.register_blueprint(tracking_bp)

    # -------------------------------
    # HTTP error handlers (reduce noise from expected 404s)
    # -------------------------------
    @app.errorhandler(NotFound)
    def handle_404(e: NotFound):
        """Return a compact JSON 404 response and log at info level.

        We intentionally avoid logging 404s as errors because they are expected
        in various scenarios (e.g., missing favicon or probing by clients).
        """
        # Do not log 404 as ERROR; it's expected sometimes (e.g., favicon)
        app.logger.info(f"404 Not Found: {getattr(e, 'description', 'Resource not found')}")
        return jsonify({
            "success": False,
            "error": "Not Found",
            "code": 404
        }), 404

    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        """Handle Werkzeug HTTP exceptions with a JSON body.

        Logs 4xx as warnings and 5xx as errors. Returns a consistent JSON
        structure with the HTTP status code.
        """
        # Generic HTTP exceptions (4xx/5xx with an HTTP code)
        level = app.logger.warning if 400 <= e.code < 500 else app.logger.error
        level(f"HTTP {e.code}: {e.description}")
        return jsonify({
            "success": False,
            "error": e.description,
            "code": e.code
        }), e.code

    # -------------------------------
    # Global JSON error handler (non-HTTP exceptions)
    # -------------------------------
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Catch-all exception handler returning JSON 500.

        Any uncaught exception will be logged with a stack trace, and the
        client receives a generic 500 response without internal details.
        """
        app.logger.exception(f"Unhandled exception: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "code": 500
        }), 500

    # -------------------------------
    # Health & version
    # -------------------------------
    @app.route("/ping")
    def ping():
        """Simple health endpoint used by uptime checks and tests."""
        return jsonify({"success": True, "status": "ok", "message": "QRWaver API online"})

    @app.route("/version")
    def version():
        """Return static application version/build information."""
        return jsonify({
            "success": True,
            "version": "1.0.0",
            "build": "backend-stable"
        })

    # Quiet favicon 404 noise if no static favicon is present
    @app.route('/favicon.ico')
    def favicon():
        """Return 204 for favicon when no static icon is present."""
        # If you add a static favicon later, replace with send_from_directory
        return "", 204

    # ---------------------------------
    # Legacy image paths redirect to R2
    # ---------------------------------
    @app.get('/users/<int:user_id>/<path:filename>')
    def legacy_user_file(user_id: int, filename: str):
        """Redirect legacy local file paths to the public CDN.

        This keeps previously shared links working by issuing a 302 to the
        configured Cloudflare R2 public base URL.
        """
        from flask import redirect
        base = (R2_PUBLIC_BASE_URL or '').rstrip('/')
        if not base:
            # No CDN configured; return 404 gracefully
            app.logger.info("R2_PUBLIC_BASE_URL not set; cannot redirect legacy /users path")
            return jsonify({"success": False, "error": "Not Found", "code": 404}), 404
        target = f"{base}/users/{user_id}/{filename}"
        return redirect(target, code=302)

    # -------------------------------
    # Development helper: auto-create tables for SQLite only
    # Avoid running this on PostgreSQL since we use Alembic migrations there.
    # -------------------------------
    with app.app_context():
        try:
            dialect = db.engine.dialect.name  # 'sqlite', 'postgresql', etc.
        except Exception:
            dialect = None

        if dialect == "sqlite":
            # Import models so SQLAlchemy knows about tables
            from app.models.user import User  # noqa: F401
            from app.models.qr_code import QRCode  # noqa: F401
            from app.models.qr_scan import QRScan  # noqa: F401
            try:
                db.create_all()
                app.logger.info("✅ (sqlite) DB tables ensured via db.create_all()")
            except Exception as e:
                app.logger.error(f"❌ DB init error (sqlite create_all): {e}")
        else:
            app.logger.info("⏭️  Skipping db.create_all() (dialect != sqlite). Use Alembic migrations.")

    return app
