import os
import logging


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "api.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


class Config:
    """
    Represents configuration settings for an application.

    This class defines a set of configuration attributes that can be used
    to manage application behavior for various environments (e.g., development,
    testing, production). Configuration values are populated from environment
    variables or fall back to default settings.

    :ivar SECRET_KEY: Secret key used for cryptographic operations.
    :type SECRET_KEY: str
    :ivar DEBUG: Specifies whether debug mode is enabled. This is determined
        by an environment variable and defaults to "True".
    :type DEBUG: bool
    :ivar TESTING: Indicates whether the application is running in a testing
        context. Default is False.
    :type TESTING: bool
    """
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")
    TESTING = False


class DevelopmentConfig(Config):
    """
    Configuration class for development environment.

    This class extends the base `Config` class and provides settings specific
    to the development environment, such as enabling debugging features and
    setting the appropriate environment type.

    :ivar ENV: The environment type, set to "development".
    :type ENV: str
    :ivar DEBUG: A flag indicating whether debugging is enabled.
    :type DEBUG: bool
    """
    ENV = "development"
    DEBUG = True


class ProductionConfig(Config):
    """
    Configuration class for the production environment.

    This class is used to define specific settings and attributes for
    the production environment. It inherits from the `Config` class,
    which presumably provides base configuration settings. The
    `ProductionConfig` class customizes the environment and enables
    or disables features as required for production usage.

    :cvar ENV: The environment name for the configuration.
    :cvar DEBUG: Flag for enabling or disabling debugging features.
    """
    ENV = "production"
    DEBUG = False
