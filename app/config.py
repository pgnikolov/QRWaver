import os

class Settings:
    ENV = os.getenv("ENV", "development")
    SECRET_KEY = os.getenv("SECRET_KEY", "qrweaver-dev-key-2023")
    MAX_QR_SIZE = int(os.getenv("MAX_QR_SIZE", "1024"))
    DEFAULT_QR_SIZE = 300
    DEFAULT_CORNER_RADIUS = 40

settings = Settings()
