from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable, defaults to SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./art_oem.db"  # Default SQLite database for development
)

# Create SQLAlchemy engine
# For SQLite, we need to set check_same_thread to False
# For PostgreSQL in production, remove the connect_args
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()


# Dependency to get database session
def get_db() -> Generator:
    """
    FastAPI dependency that provides a database session.
    Ensures the session is closed after the request is complete.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to create all tables
def create_tables():
    """
    Create all database tables.
    Should be called on application startup or via migration.
    """
    Base.metadata.create_all(bind=engine)
