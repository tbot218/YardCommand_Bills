# backend/db/database.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------------------------
# DATABASE URL (SQLite)
# -------------------------
database_url = os.getenv("DATABASE_URL", "sqlite:///./yardcommand.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# -------------------------
# ENGINE
# -------------------------
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
)

# -------------------------
# SESSION
# -------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -------------------------
# BASE MODEL
# -------------------------
Base = declarative_base()


# -------------------------
# DEPENDENCY FOR FASTAPI
# -------------------------
def get_db():
    """
    Yields a SQLAlchemy database session.
    Used by FastAPI dependency injection.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
