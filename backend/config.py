import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "smart_manufacturing_secret")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "manufacturing_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "SQLALCHEMY_DATABASE_URI",
            "sqlite:///./smart_manufacturing.db"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False