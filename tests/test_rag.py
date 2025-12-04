
import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.core.vector_store import VectorStore, VectorStoreConfig
    from backend.core.rag_engine import RAGEngine, RAGConfig
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
        rag = RAGEngine(store)
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

        store.add_documents(docs, metadatas)
        print("[PASS] Documents added")

        # Test Context Retrieval
        query = "What is the capital of France?"
        context = rag.retrieve_context(query)

        assert "Paris" in context
        assert "Source: geography_book" in context
        print("[PASS] Context retrieval passed")

        # Test Prompt Augmentation
        augmented = rag.augment_prompt(query, "Answer the question.")

        assert "Relevant Context:" in augmented
        assert "Paris" in augmented
        assert "Answer the question." in augmented
        print("[PASS] Prompt augmentation passed")

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
