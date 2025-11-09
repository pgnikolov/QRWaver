from flask import Flask
from app.routes.main_routes import main_bp
from app.routes.qr_routes import qr_bp
from app.routes.api_routes import api_bp
from app.config.settings import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Регистрация на blueprint-и
    app.register_blueprint(main_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(api_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    print("🚀 QRWeaver backend running")
    print("📍 http://127.0.0.1:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
