from flask import Flask
import os


def create_app():
    """
    Creates and configures an instance of the Flask application. This function initializes
    the main application by setting up configuration options, registering blueprints, and
    preparing necessary application-level settings.

    :raises RuntimeError: If the Flask application fails to initiate due to missing or
        misconfigured components.

    :return: An instance of the Flask application configured and ready for use.
    :rtype: Flask
    """
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'qrweaver-dev-key-2023'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)

    return app
