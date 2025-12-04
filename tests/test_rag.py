
import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import sys
    from pathlib import Path
    # Add packages to path for testing
    sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "core" / "src"))
    from vector_store import VectorStore, VectorStoreConfig
    from rag import RAGEngine
except ImportError as e:
    print(f"[FAIL] Import Error: {e}")
    sys.exit(1)

def test_rag_engine():
    print("Testing RAG Engine...")

    # Setup test config
    test_db_path = "./test_rag_db"
    vs_config = VectorStoreConfig(
        path=test_db_path,
        collection_name="test_rag_collection"
    )

    # Clean up
    if os.path.exists(test_db_path):
        try:
            shutil.rmtree(test_db_path)
        except:
            pass

    try:
        # Initialize
        store = VectorStore(vs_config)
        rag = RAGEngine(persist_directory=test_db_path, collection_name="test_rag_collection")
        print("[PASS] Initialization passed")

        # Add documents
        docs = [
            "The capital of France is Paris.",
            "The capital of Germany is Berlin.",
            "Water boils at 100 degrees Celsius."
        ]
        metadatas = [
            {"source": "geography_book"},
            {"source": "geography_book"},
            {"source": "science_book"}
        ]
        ids = ["doc1", "doc2", "doc3"]

        rag.add_documents(docs, metadatas, ids)
        print("[PASS] Documents added")

        # Test Search
        query = "What is the capital of France?"
        results = rag.search(query, n_results=1)

        assert len(results) > 0
        assert "Paris" in results[0].document
        print("[PASS] Search passed")

        # Search test already passed above

    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if os.path.exists(test_db_path):
            try:
                shutil.rmtree(test_db_path)
            except:
                print("Warning: Cleanup failed (file lock)")

if __name__ == "__main__":
    test_rag_engine()
