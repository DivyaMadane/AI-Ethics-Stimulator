from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import NullPool
from .config import settings

# Use NullPool for local dev to avoid connection reuse issues on Windows
# Add SQLite-friendly connect_args when using sqlite
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
        future=True,
    )
else:
    engine = create_engine(settings.database_url, poolclass=NullPool, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

# Dependency for FastAPI routes

def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
