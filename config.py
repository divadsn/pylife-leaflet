import os

# App settings
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
DEBUG = os.environ.get("DEBUG", "True").lower() in ("yes", "true", "t", "1")
SECRET_KEY = os.environ.get("SECRET_KEY", "1B0Mm63J5k6yRRIW")
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:example@localhost:5432/postgres")

# JSON Encoder settings
JSON_SORT_KEYS = False
JSON_AS_ASCII = False

# SQL Alchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False
