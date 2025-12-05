import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))
# Add packages paths
sys.path.insert(0, str(Path(__file__).parent / "packages" / "memory" / "src"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "core" / "src"))

try:
    from codeops.memory.rag_engine import RAGEngine
except ImportError as e:
    print(f"Import Error: {e}")
    # Try to debug path
    print(f"Sys Path: {sys.path}")
    sys.exit(1)

def test_chroma():
    print("Testing ChromaDB Backend...")
    try:
        engine = RAGEngine(vector_store_type="chroma")
        engine.ingest(
            documents=["This is a test document about RAG.", "ChromaDB is a vector database."],
            metadatas=[{"source": "test"}, {"source": "test"}],
            ids=["doc1", "doc2"]
        )
        results = engine.query("vector database")
        print("Chroma Results:", results)

        # Check if doc2 is in the results
        # Chroma returns list of lists
        found = False
        if results and "ids" in results:
            for id_list in results["ids"]:
                if "doc2" in id_list:
                    found = True
                    break

        if found:
            print("PASS: ChromaDB retrieval successful.")
        else:
            print("FAIL: ChromaDB retrieval failed to find expected document.")

    except Exception as e:
        print(f"FAIL: ChromaDB test error: {e}")

def test_faiss():
    print("\nTesting FAISS Backend...")
    try:
        engine = RAGEngine(vector_store_type="faiss")
        engine.ingest(
            documents=["FAISS is fast.", "In-memory vector search."],
            metadatas=[{"tag": "fast"}, {"tag": "memory"}],
            ids=["f1", "f2"]
        )
        results = engine.query("fast search")
        print("FAISS Results:", results)

        found = False
        if results and "ids" in results:
            for id_list in results["ids"]:
                if "f1" in id_list:
                    found = True
                    break

        if found:
            print("PASS: FAISS retrieval successful.")
        else:
            print("FAIL: FAISS retrieval failed to find expected document.")

    except ImportError:
        print("SKIP: FAISS/SentenceTransformers not installed.")
    except Exception as e:
        print(f"FAIL: FAISS test error: {e}")

if __name__ == "__main__":
    test_chroma()
    test_faiss()
