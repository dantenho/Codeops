"""
Index .gitcommit document to ChromaDB with vectorization.

This script:
1. Reads the .gitcommit convention document
2. Chunks it into meaningful sections
3. Creates embeddings using sentence-transformers
4. Stores in ChromaDB with metadata
5. Enables RAG queries for git workflow assistance
"""

import sys
from pathlib import Path
from typing import List, Dict
import re

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class GitCommitIndexer:
    """Index git commit convention document to ChromaDB."""

    def __init__(self, chromadb_path: str = None):
        """Initialize indexer with ChromaDB client."""
        if chromadb_path is None:
            chromadb_path = str(project_root / ".chromadb")

        self.client = chromadb.PersistentClient(
            path=chromadb_path,
            settings=Settings(anonymized_telemetry=False)
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="git_commit_convention",
            metadata={"description": "Git commit convention and workflow documentation"}
        )

        # Load embedding model
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Model loaded")

    def read_gitcommit_file(self, file_path: Path) -> str:
        """Read the .gitcommit file."""
        print(f"Reading {file_path}...")
        content = file_path.read_text(encoding='utf-8')
        print(f"✓ Read {len(content)} characters")
        return content

    def chunk_document(self, content: str) -> List[Dict[str, str]]:
        """
        Chunk the document into logical sections.

        Returns list of chunks with metadata:
        - text: The chunk content
        - section: Section name
        - category: Type of content (format, types, scopes, workflow, etc.)
        """
        chunks = []

        # Split by major headers (##)
        sections = re.split(r'\n## ', content)

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # First section doesn't have ## prefix
            if i == 0:
                lines = section.split('\n')
                header = lines[0].replace('# ', '')
                text = '\n'.join(lines[1:]).strip()
            else:
                lines = section.split('\n')
                header = lines[0].strip()
                text = '\n'.join(lines[1:]).strip()

            if not text:
                continue

            # Determine category
            category = self._categorize_section(header)

            # Further split large sections by ### headers
            subsections = re.split(r'\n### ', text)

            for j, subsection in enumerate(subsections):
                if not subsection.strip():
                    continue

                if j == 0:
                    # First subsection (before any ###)
                    chunk_text = subsection.strip()
                    subsection_header = header
                else:
                    # Subsection with ### header
                    sub_lines = subsection.split('\n')
                    subsection_header = f"{header} - {sub_lines[0].strip()}"
                    chunk_text = '\n'.join(sub_lines[1:]).strip()

                if chunk_text and len(chunk_text) > 50:  # Skip very small chunks
                    chunks.append({
                        'text': chunk_text,
                        'section': subsection_header,
                        'category': category,
                        'header': header
                    })

        print(f"✓ Created {len(chunks)} chunks")
        return chunks

    def _categorize_section(self, header: str) -> str:
        """Categorize section by header."""
        header_lower = header.lower()

        if 'format' in header_lower:
            return 'format'
        elif 'type' in header_lower:
            return 'types'
        elif 'scope' in header_lower:
            return 'scopes'
        elif 'example' in header_lower:
            return 'examples'
        elif 'branch' in header_lower:
            return 'branches'
        elif 'workflow' in header_lower:
            return 'workflows'
        elif 'best practice' in header_lower:
            return 'best_practices'
        elif 'troubleshoot' in header_lower:
            return 'troubleshooting'
        elif 'lock' in header_lower or 'coordination' in header_lower:
            return 'coordination'
        else:
            return 'general'

    def create_embeddings(self, chunks: List[Dict[str, str]]) -> List[List[float]]:
        """Create embeddings for all chunks."""
        print("Creating embeddings...")
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"✓ Created {len(embeddings)} embeddings")
        return embeddings.tolist()

    def index_to_chromadb(self, chunks: List[Dict[str, str]], embeddings: List[List[float]]):
        """Index chunks with embeddings to ChromaDB."""
        print("Indexing to ChromaDB...")

        # Clear existing collection
        existing_count = self.collection.count()
        if existing_count > 0:
            print(f"  Clearing {existing_count} existing documents...")
            # Delete all by getting all IDs
            all_docs = self.collection.get()
            if all_docs['ids']:
                self.collection.delete(ids=all_docs['ids'])

        # Prepare data
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'section': chunk['section'],
                'category': chunk['category'],
                'header': chunk['header']
            }
            for chunk in chunks
        ]

        # Add to collection
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        print(f"✓ Indexed {len(chunks)} documents to ChromaDB")
        print(f"  Collection: {self.collection.name}")
        print(f"  Total documents: {self.collection.count()}")

    def test_query(self, query: str, n_results: int = 3):
        """Test a query against the indexed documents."""
        print(f"\nTest Query: '{query}'")
        print("-" * 60)

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                print(f"\nResult {i+1}:")
                print(f"  Section: {metadata['section']}")
                print(f"  Category: {metadata['category']}")
                print(f"  Text: {doc[:150]}...")
        else:
            print("  No results found")

    def run(self, gitcommit_path: Path):
        """Run the full indexing pipeline."""
        print("\n" + "=" * 60)
        print("GIT COMMIT CONVENTION INDEXER")
        print("=" * 60 + "\n")

        # Read file
        content = self.read_gitcommit_file(gitcommit_path)

        # Chunk document
        chunks = self.chunk_document(content)

        # Create embeddings
        embeddings = self.create_embeddings(chunks)

        # Index to ChromaDB
        self.index_to_chromadb(chunks, embeddings)

        # Test queries
        print("\n" + "=" * 60)
        print("TEST QUERIES")
        print("=" * 60)

        test_queries = [
            "How do I create a commit message?",
            "What is the branch naming convention?",
            "How do I handle merge conflicts?",
            "What are the different commit types?",
            "How do I use branch locks?"
        ]

        for query in test_queries:
            self.test_query(query, n_results=2)
            print()

        print("\n" + "=" * 60)
        print("INDEXING COMPLETE")
        print("=" * 60)
        print(f"\nChromaDB collection: {self.collection.name}")
        print(f"Total documents: {self.collection.count()}")
        print(f"Embedding dimension: 384")
        print("\nYou can now use this collection for RAG queries!")


def main():
    """Main entry point."""
    gitcommit_path = project_root / ".gitcommit"

    if not gitcommit_path.exists():
        print(f"Error: {gitcommit_path} not found!")
        sys.exit(1)

    indexer = GitCommitIndexer()
    indexer.run(gitcommit_path)


if __name__ == "__main__":
    main()
