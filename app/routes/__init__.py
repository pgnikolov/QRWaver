from .main_routes import main_bp
from .api_routes import api_bp
from .qr_routes import qr_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(qr_bp)
