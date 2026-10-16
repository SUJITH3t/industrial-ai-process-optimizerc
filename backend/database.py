from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config

# Create Database Engine
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    echo=True
)

# Session Factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Function to get database session
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()