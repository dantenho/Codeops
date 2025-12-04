
import sys
print("Importing embedding functions...")
try:
    from chromadb.utils import embedding_functions
    print("Imported embedding_functions.")

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    print("Embedding function created.")

    embeddings = ef(["This is a test."])
    print(f"Embeddings generated: {len(embeddings)}")
except Exception as e:
    print(f"Error: {e}")
