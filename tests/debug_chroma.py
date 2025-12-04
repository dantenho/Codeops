
import sys
print("Importing chromadb...")
try:
    import chromadb
    print("Chromadb imported successfully.")
    client = chromadb.Client()
    print("Client created.")
except Exception as e:
    print(f"Error: {e}")
