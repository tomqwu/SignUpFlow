"""Database configuration and session management."""

import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from api.models import Base
from api.core.config import settings

# Database URL - can be configured via environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./roster.db")

# Create engine with SQLite optimizations
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
        "timeout": 30,  # Increase timeout to 30 seconds for better concurrency
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,  # Verify connections before using them
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables."""
    if settings.TESTING or os.getenv("TESTING"):
        print(f"[init_db] cwd={os.getcwd()} DATABASE_URL={DATABASE_URL}")
    Base.metadata.create_all(bind=engine)

    # Enable WAL mode for better concurrency in SQLite unless running tests
    if DATABASE_URL.startswith("sqlite"):
        env_testing = os.getenv("TESTING", "").lower() in {"1", "true", "yes", "on"}
        with engine.connect() as conn:
            if settings.TESTING or env_testing:
                conn.execute(text("PRAGMA journal_mode=DELETE"))
            else:
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.execute(text("PRAGMA synchronous=NORMAL"))  # Balance between safety and performance
            conn.commit()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Usage in FastAPI route:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
