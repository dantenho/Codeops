from codeops.core.config import settings
from sqlmodel import SQLModel, create_engine

# Use SQLite by default if DATABASE_URL is not set
DATABASE_URL = settings.DATABASE_URL or "sqlite:///database.db"

engine = create_engine(DATABASE_URL, echo=settings.DEBUG)

def init_db():
    """Initialize the database tables."""
    SQLModel.metadata.create_all(engine)
