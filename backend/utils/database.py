from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
import tempfile
from pathlib import Path

# Use system temp directory (always writable)
TEMP_DIR = Path(tempfile.gettempdir()) / "cc_parser"
TEMP_DIR.mkdir(exist_ok=True)
DATABASE_PATH = TEMP_DIR / "database.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

print(f"📂 Using database at: {DATABASE_PATH}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from models import Base
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database created at: {DATABASE_PATH}")