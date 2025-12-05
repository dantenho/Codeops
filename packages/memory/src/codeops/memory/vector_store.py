import chromadb
from chromadb.config import Settings
from codeops.core.config import settings
from codeops.core.exceptions import RAGError


class VectorStore:
    """Wrapper for ChromaDB vector store."""

    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=Settings(allow_reset=True)
            )
            self.collection = self.client.get_or_create_collection("codebase")
        except Exception as e:
            raise RAGError(f"Failed to initialize ChromaDB: {str(e)}")

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        """Add documents to the vector store."""
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            raise RAGError(f"Failed to add documents: {str(e)}")

    def search(self, query: str, n_results: int = 5):
        """Search for similar documents."""
        try:
            return self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
        except Exception as e:
            raise RAGError(f"Failed to search documents: {str(e)}")
