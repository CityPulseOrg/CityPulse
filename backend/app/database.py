"""
CityPulse Database Configuration
SQLAlchemy setup for PostgreSQL connection.
"""
# DOCS:
# - UGly ahh sqlalchemy doc: https://docs.sqlalchemy.org/en/20/tutorial/index.html 
# - FastAPI + SQLAlchemy: https://fastapi.tiangolo.com/tutorial/sql-databases/

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

#Create engine 
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections are alive
)

#Session factory 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base class
Base = declarative_base()

def get_db():
    """
    FastAPI dependency that provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
