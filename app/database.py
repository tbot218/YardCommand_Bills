from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use /tmp for SQLite on Render (writable directory)
DATABASE_URL = "sqlite:////tmp/bills.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
