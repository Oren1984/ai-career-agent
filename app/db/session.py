# db/session.py
# this file initializes the database connection and provides access to the database session

"""Database session management and initialization."""
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "jobs.db",
)

_DB_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}")


def get_engine(db_url: str | None = None):
    url = db_url or _DB_URL
    os.makedirs(os.path.dirname(url.replace("sqlite:///", "")), exist_ok=True)
    return create_engine(url, connect_args={"check_same_thread": False})


def init_db(db_url: str | None = None) -> None:
    """Create all tables if they don't exist."""
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)
    logger.info("Database initialized at %s", db_url or _DB_URL)


def get_session(db_url: str | None = None) -> Session:
    """Return a new SQLAlchemy session."""
    engine = get_engine(db_url)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return SessionLocal()


def get_session_factory(db_url: str | None = None):
    """Return the session factory for dependency injection."""
    engine = get_engine(db_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
