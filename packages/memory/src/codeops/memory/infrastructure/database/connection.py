"""
Infrastructure Layer: Database Connection

Handles database connection and engine creation.
"""
from sqlmodel import create_engine, SQLModel
from typing import Optional


class DatabaseConnection:
    """Database connection manager."""

    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize database connection.

        Args:
            database_url: Database connection URL
            echo: Whether to echo SQL statements
        """
        self.database_url = database_url
        self.echo = echo
        self._engine: Optional[object] = None

    def get_engine(self):
        """
        Get or create database engine.

        Returns:
            SQLModel engine instance
        """
        if self._engine is None:
            self._engine = create_engine(self.database_url, echo=self.echo)
        return self._engine

    def create_tables(self):
        """Create all database tables."""
        SQLModel.metadata.create_all(self.get_engine())

    def drop_tables(self):
        """Drop all database tables (use with caution!)."""
        SQLModel.metadata.drop_all(self.get_engine())

    def reset_database(self):
        """Reset database by dropping and recreating all tables."""
        self.drop_tables()
        self.create_tables()
