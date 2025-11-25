"""Application extensions setup.

This module defines and initializes reusable Flask extensions used across
the application: SQLAlchemy for database access, JWTManager for auth,
Flask-Migrate for migrations, and CORS for cross-origin requests.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def init_extensions(app):
    """Initialize core Flask extensions on the given app instance.

    - Binds SQLAlchemy to the app
    - Enables JWT support
    - Wires Flask-Migrate with the database
    - Enables CORS with credential support
    """
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True)
