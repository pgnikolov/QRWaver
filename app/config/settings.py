import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
