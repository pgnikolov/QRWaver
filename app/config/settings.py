"""Application configuration settings.

Loads environment variables, defines constants for external services (e.g.,
Cloudflare R2, Google OAuth), and exposes configuration classes for different
environments (development/production).
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "api.log")

# ---------------------------------------
# Cloudflare R2
# ---------------------------------------
R2_BUCKET = os.getenv("R2_BUCKET")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
R2_PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL", "").rstrip("/")

# ---------------------------------------
# Public base URL for short links
# ---------------------------------------
# If set, this will be used as the base for trackable short URLs embedded in QR codes,
# e.g. https://yourdomain.com/s/<slug>. If not set, we fall back to request.host_url.
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").strip()

# ---------------------------------------
# Google OAuth
# ---------------------------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_CLOCK_SKEW_SECONDS = int(os.getenv("GOOGLE_CLOCK_SKEW_SECONDS", "180") or 180)


class Config:
    """Base configuration shared by all environments."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///qrwaver.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev_jwt_secret")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_HTTPONLY = True
    # In development we keep cookies non-secure; ProductionConfig overrides to True
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = "Lax"
    # Allow small clock skew when validating JWTs to avoid "Token used too early" errors
    # ProductionConfig tightens this to 30s.
    JWT_DECODE_LEEWAY = 60  # seconds

    JWT_COOKIE_CSRF_PROTECT = False


class DevelopmentConfig(Config):
    """Development defaults: debug enabled and relaxed JWT settings."""
    ENV = "development"
    DEBUG = True


class ProductionConfig(Config):
    """Production defaults: debug disabled and stricter JWT settings."""
    ENV = "production"
    DEBUG = False
    # Harden cookies for production
    JWT_COOKIE_SECURE = True
    # Tighter leeway in production
    JWT_DECODE_LEEWAY = 30
