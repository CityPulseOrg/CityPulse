"""
CityPulse Database Configuration

================================================================================
TODO: Backend team (Zak/Bala) - Set up SQLAlchemy database connection here.

REQUIREMENTS:
1. Import DATABASE_URL from app/config.py (get_settings().database_url)
2. Create SQLAlchemy engine with the database URL
3. Create SessionLocal for database sessions
4. Create Base class for models to inherit from
5. Create get_db() dependency for FastAPI route injection

DATABASE_URL FORMAT (already wired in docker-compose):
    postgresql://citypulse:citypulse@db:5432/citypulse

DOCS:
- UGly ahh sqlalchemy doc: https://docs.sqlalchemy.org/en/20/tutorial/index.html 
- FastAPI + SQLAlchemy: https://fastapi.tiangolo.com/tutorial/sql-databases/
================================================================================
"""

# Implement database setup here
