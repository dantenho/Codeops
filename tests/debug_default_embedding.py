
import sys
import chromadb
from chromadb.utils import embedding_functions

print("Testing DefaultEmbeddingFunction...")
try:
    # This usually uses ONNX MiniLM
    ef = embedding_functions.DefaultEmbeddingFunction()
    print("DefaultEmbeddingFunction created.")

    embeddings = ef(["This is a test."])
    print(f"Embeddings generated: {len(embeddings)}")
except Exception as e:
    print(f"Error: {e}")
