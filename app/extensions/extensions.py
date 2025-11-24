from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def init_extensions(app):
    """Initialise SQLAlchemy, JWT, Migrate & CORS"""
    db.init_app(app)
    jwt.init_app(app)

    migrate.init_app(app, db)

    CORS(app, supports_credentials=True)
