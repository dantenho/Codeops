
import sys
import os
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
<<<<<<< Current (Your changes)
    from CodeAgents.core.rag import RAGEngine, get_rag_engine
    # Note: VectorStore functionality is now part of RAGEngine
=======
    from eudorax.core.vector_store import VectorStore, VectorStoreConfig
>>>>>>> Incoming (Background Agent changes)
except ImportError as e:
    print(f"[FAIL] Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[FAIL] Unexpected Error during import: {e}")
    sys.exit(1)

def test_vector_store():
    print("Testing Vector Store...")

    # Setup test config
    test_db_path = "./test_chroma_db"
    config = VectorStoreConfig(
        path=test_db_path,
        collection_name="test_collection"
    )

    # Clean up previous test run
    if os.path.exists(test_db_path):
        try:
            shutil.rmtree(test_db_path)
        except PermissionError:
            print(f"Warning: Could not delete {test_db_path} (locked). Using existing.")
        except Exception:
            pass

    try:
        # Initialize
        store = VectorStore(config)
        print("[PASS] Initialization passed")

        # Add documents
        docs = ["This is a test document about AI.", "Python is a programming language."]
        metadatas = [{"topic": "ai"}, {"topic": "coding"}]
        ids = ["doc1", "doc2"]

        store.add_documents(docs, metadatas, ids)
        print("[PASS] Add documents passed")

        # Query
        results = store.query("artificial intelligence", n_results=1)

        assert len(results['ids'][0]) > 0
        assert results['ids'][0][0] == "doc1"
        print("[PASS] Query passed")

    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if os.path.exists(test_db_path):
            try:
                shutil.rmtree(test_db_path)
            except PermissionError:
                print(f"Warning: Could not delete {test_db_path} due to file lock. This is expected on Windows.")
            except Exception as e:
                print(f"Warning: Cleanup failed: {e}")

if __name__ == "__main__":
    test_vector_store()
