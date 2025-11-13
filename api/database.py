"""Database configuration and session management."""

import os
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
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


def _resolve_sqlite_path(db_url: str) -> Optional[Path]:
    """Translate SQLite URLs into filesystem paths."""
    if not db_url.startswith("sqlite"):
        return None
    url = make_url(db_url)
    database = url.database or ""
    path = Path(database)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def _prepare_sqlite_file(sqlite_path: Path, db_url: str) -> None:
    """Ensure the SQLite file and parent directories exist with write access."""
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    sqlite_path.touch(exist_ok=True)
    # Always set permissions (touch doesn't update existing file permissions)
    sqlite_path.chmod(0o666)  # rw-rw-rw- for maximum compatibility in tests
    if settings.TESTING or os.getenv("TESTING"):
        stats = sqlite_path.stat()
        print(
            f"[init_db] ensuring sqlite database at {sqlite_path} (from {db_url}) "
            f"(mode={oct(stats.st_mode & 0o777)} owner={stats.st_uid}:{stats.st_gid})"
        )


def init_db() -> None:
    """Initialize database tables."""
    sqlite_path = _resolve_sqlite_path(DATABASE_URL)
    if sqlite_path:
        _prepare_sqlite_file(sqlite_path, DATABASE_URL)
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
