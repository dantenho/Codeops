"""
Infrastructure Layer: Database Session Management

Handles database session lifecycle.
"""
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session

from .connection import DatabaseConnection


class SessionManager:
    """Database session manager."""

    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize session manager.

        Args:
            db_connection: Database connection instance
        """
        self.db_connection = db_connection

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session context manager.

        Yields:
            SQLModel session

        Example:
            with session_manager.get_session() as session:
                # Use session
                pass
        """
        session = Session(self.db_connection.get_engine())
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_session(self) -> Session:
        """
        Create a new database session.

        Returns:
            SQLModel session

        Note:
            Caller is responsible for closing the session.
        """
        return Session(self.db_connection.get_engine())
