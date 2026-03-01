"""Database service"""

from typing import Optional, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from jartbrowser.core.config import get_settings
from jartbrowser.models.database import Base


class DatabaseService:
    """Database connection and session management"""

    def __init__(self, database_url: Optional[str] = None):
        settings = get_settings()
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {},
            pool_pre_ping=True,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables"""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_session_dependency(self) -> Generator[Session, None, None]:
        """Dependency for FastAPI"""
        with self.get_session() as session:
            yield session


# Global instance
_database_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get global database service"""
    global _database_service
    if _database_service is None:
        _database_service = DatabaseService()
    return _database_service
