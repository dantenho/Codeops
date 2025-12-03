"""
Database module for the Agent Training System.
Provides backward-compatible accessors while delegating to the new hierarchical
data layer.
"""

from .data.client import ChromaDatabase

db = ChromaDatabase()

# Legacy exports maintained for compatibility
client = db.client
training_collection = db.collections.training
error_collection = db.collections.errors
score_collection = db.collections.scores
daily_log_collection = db.collections.daily_logs


def get_db_client():
    """Returns the ChromaDB client."""
    return client


def get_database() -> ChromaDatabase:
    """Return the structured database wrapper."""
    return db
