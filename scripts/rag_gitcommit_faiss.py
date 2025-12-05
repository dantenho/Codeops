"""
RAG System for Git Commit Convention using FAISS GPU and Memory Integration.

This implements:
1. FAISS GPU-accelerated vector search
2. ChromaDB integration for document storage
3. Memory system integration for context tracking
4. RAG pipeline for intelligent Q&A
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

try:
    import faiss
    FAISS_AVAILABLE = True

    # Check if GPU is available
    try:
        faiss.StandardGpuResources()
        FAISS_GPU_AVAILABLE = True
    except:
        FAISS_GPU_AVAILABLE = False
except ImportError:
    FAISS_AVAILABLE = False
    FAISS_GPU_AVAILABLE = False


class GitCommitRAG:
    """RAG system for git commit convention with FAISS GPU acceleration."""

    def __init__(
        self,
        chromadb_path: str = None,
        use_faiss: bool = True,
        use_gpu: bool = True
    ):
        """
        Initialize RAG system.

        Args:
            chromadb_path: Path to ChromaDB storage
            use_faiss: Use FAISS for faster similarity search
            use_gpu: Use GPU acceleration for FAISS
        """
        # ChromaDB setup
        if chromadb_path is None:
            chromadb_path = str(project_root / ".chromadb")

        self.client = chromadb.PersistentClient(
            path=chromadb_path,
            settings=Settings(anonymized_telemetry=False)
        )

        try:
            self.collection = self.client.get_collection("git_commit_convention")
            print(f"✓ Connected to ChromaDB collection: {self.collection.name}")
            print(f"  Documents: {self.collection.count()}")
        except Exception as e:
            print(f"✗ Collection not found. Run index_gitcommit_to_chromadb.py first!")
            raise e

        # Load embedding model
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Model loaded")

        # FAISS setup
        self.use_faiss = use_faiss and FAISS_AVAILABLE
        self.use_gpu = use_gpu and FAISS_GPU_AVAILABLE

        if self.use_faiss:
            self._setup_faiss()
        else:
            if not FAISS_AVAILABLE:
                print("⚠ FAISS not available. Install: pip install faiss-cpu or faiss-gpu")
            print("Using ChromaDB native search")

        # Memory system (for conversation context)
        self.conversation_history: List[Dict] = []

    def _setup_faiss(self):
        """Setup FAISS index from ChromaDB embeddings."""
        print("\nSetting up FAISS index...")

        # Get all embeddings from ChromaDB
        all_data = self.collection.get(include=['embeddings', 'documents', 'metadatas'])

        if all_data['embeddings'] is None or len(all_data['embeddings']) == 0:
            print("✗ No embeddings found in ChromaDB")
            self.use_faiss = False
            return

        # Convert to numpy array
        embeddings = np.array(all_data['embeddings'], dtype=np.float32)
        self.doc_ids = all_data['ids']
        self.documents = all_data['documents']
        self.metadatas = all_data['metadatas']

        dimension = embeddings.shape[1]
        n_docs = embeddings.shape[0]

        print(f"  Embeddings shape: {embeddings.shape}")
        print(f"  Dimension: {dimension}")
        print(f"  Documents: {n_docs}")

        # Create FAISS index
        if self.use_gpu:
            try:
                # GPU index
                print("  Creating FAISS GPU index...")
                res = faiss.StandardGpuResources()

                # Create CPU index first
                cpu_index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)

                # Move to GPU
                self.index = faiss.index_cpu_to_gpu(res, 0, cpu_index)

                # Normalize vectors for cosine similarity
                faiss.normalize_L2(embeddings)

                # Add vectors
                self.index.add(embeddings)

                print(f"✓ FAISS GPU index created with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"✗ GPU setup failed: {e}")
                print("  Falling back to CPU...")
                self.use_gpu = False
                self._setup_faiss_cpu(embeddings, dimension)
        else:
            self._setup_faiss_cpu(embeddings, dimension)

    def _setup_faiss_cpu(self, embeddings: np.ndarray, dimension: int):
        """Setup FAISS CPU index."""
        print("  Creating FAISS CPU index...")

        # Create index
        self.index = faiss.IndexFlatIP(dimension)  # Inner product

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        # Add vectors
        self.index.add(embeddings)

        print(f"✓ FAISS CPU index created with {self.index.ntotal} vectors")

    def search(
        self,
        query: str,
        n_results: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for relevant documents.

        Args:
            query: Search query
            n_results: Number of results to return
            category_filter: Filter by category (format, types, scopes, etc.)

        Returns:
            List of results with text, metadata, and scores
        """
        if self.use_faiss:
            return self._search_faiss(query, n_results, category_filter)
        else:
            return self._search_chromadb(query, n_results, category_filter)

    def _search_faiss(
        self,
        query: str,
        n_results: int,
        category_filter: Optional[str]
    ) -> List[Dict]:
        """Search using FAISS index."""
        # Create query embedding
        query_embedding = self.model.encode([query])
        query_vec = np.array(query_embedding, dtype=np.float32)
        faiss.normalize_L2(query_vec)

        # Search
        scores, indices = self.index.search(query_vec, n_results * 2)  # Get more for filtering

        # Build results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue

            metadata = self.metadatas[idx]

            # Apply category filter
            if category_filter and metadata.get('category') != category_filter:
                continue

            results.append({
                'text': self.documents[idx],
                'metadata': metadata,
                'score': float(score),
                'id': self.doc_ids[idx]
            })

            if len(results) >= n_results:
                break

        return results

    def _search_chromadb(
        self,
        query: str,
        n_results: int,
        category_filter: Optional[str]
    ) -> List[Dict]:
        """Search using ChromaDB native search."""
        where_filter = {"category": category_filter} if category_filter else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter
        )

        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0] if 'distances' in results else [0] * len(results['documents'][0])
            ):
                formatted_results.append({
                    'text': doc,
                    'metadata': metadata,
                    'score': 1.0 - distance,  # Convert distance to similarity score
                    'id': None
                })

        return formatted_results

    def generate_answer(
        self,
        query: str,
        n_results: int = 3,
        use_genai: bool = True
    ) -> Dict:
        """
        Generate answer using RAG pipeline.

        Args:
            query: User question
            n_results: Number of context documents to retrieve
            use_genai: Use Google GenAI for generation (requires API key)

        Returns:
            Dict with answer, sources, and metadata
        """
        # Search for relevant documents
        results = self.search(query, n_results)

        if not results:
            return {
                'answer': "I couldn't find relevant information in the git commit convention documentation.",
                'sources': [],
                'query': query
            }

        # Build context from retrieved documents
        context_parts = []
        sources = []

        for i, result in enumerate(results, 1):
            section = result['metadata'].get('section', 'Unknown')
            text = result['text'][:500]  # Limit length
            score = result.get('score', 0)

            context_parts.append(f"[Source {i} - {section}]:\n{text}\n")
            sources.append({
                'section': section,
                'category': result['metadata'].get('category', 'general'),
                'score': score,
                'text_preview': text[:150] + "..."
            })

        context = "\n".join(context_parts)

        # Generate answer
        if use_genai:
            answer = self._generate_with_genai(query, context)
        else:
            answer = self._generate_simple(query, context, results)

        # Add to conversation history
        self.conversation_history.append({
            'query': query,
            'answer': answer,
            'sources': sources
        })

        return {
            'answer': answer,
            'sources': sources,
            'query': query,
            'context': context[:500] + "..." if len(context) > 500 else context
        }

    def _generate_with_genai(self, query: str, context: str) -> str:
        """Generate answer using Google GenAI."""
        import os

        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            return self._generate_simple(query, context, [])

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")

            prompt = f"""You are a Git workflow assistant. Answer the user's question based ONLY on the provided context from the git commit convention documentation.

Context:
{context}

User Question: {query}

Instructions:
- Provide a clear, concise answer
- Reference specific sections when possible
- If the context doesn't contain the answer, say so
- Use examples from the context if available

Answer:"""

            response = model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"GenAI error: {e}")
            return self._generate_simple(query, context, [])

    def _generate_simple(self, query: str, context: str, results: List) -> str:
        """Generate simple answer without LLM."""
        if not results:
            return f"Based on the documentation:\n\n{context[:400]}..."

        # Extract most relevant section
        best_result = results[0] if results else None

        if best_result:
            section = best_result['metadata'].get('section', 'Git Convention')
            text = best_result['text'][:600]

            return f"""Based on the section "{section}":

{text}

For more details, refer to the full git commit convention documentation."""

        return f"Here's what I found:\n\n{context[:500]}..."

    def interactive_session(self):
        """Run interactive Q&A session."""
        print("\n" + "=" * 60)
        print("GIT COMMIT CONVENTION RAG ASSISTANT")
        print("=" * 60)
        print(f"Backend: {'FAISS GPU' if self.use_gpu else 'FAISS CPU' if self.use_faiss else 'ChromaDB'}")
        print(f"Documents indexed: {self.collection.count()}")
        print("\nAsk questions about git commit conventions and workflows.")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                query = input("Question: ").strip()

                if query.lower() in ['quit', 'exit', 'q']:
                    print("\nGoodbye!")
                    break

                if not query:
                    continue

                print("\nSearching...")
                result = self.generate_answer(query, n_results=3)

                print("\n" + "-" * 60)
                print("ANSWER:")
                print("-" * 60)
                print(result['answer'])

                print("\n" + "-" * 60)
                print("SOURCES:")
                print("-" * 60)
                for i, source in enumerate(result['sources'], 1):
                    print(f"{i}. {source['section']} (score: {source['score']:.3f})")
                    print(f"   {source['text_preview']}")

                print()

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")

    def get_memory_stats(self) -> Dict:
        """Get memory/conversation statistics."""
        return {
            'conversation_turns': len(self.conversation_history),
            'total_documents': self.collection.count(),
            'backend': 'FAISS GPU' if self.use_gpu else 'FAISS CPU' if self.use_faiss else 'ChromaDB',
            'embedding_model': 'all-MiniLM-L6-v2',
            'embedding_dimension': 384
        }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="RAG system for git commit conventions")
    parser.add_argument('--no-faiss', action='store_true', help='Disable FAISS')
    parser.add_argument('--cpu', action='store_true', help='Force CPU (no GPU)')
    parser.add_argument('--query', type=str, help='Single query mode')

    args = parser.parse_args()

    # Initialize RAG system
    rag = GitCommitRAG(
        use_faiss=not args.no_faiss,
        use_gpu=not args.cpu
    )

    if args.query:
        # Single query mode
        result = rag.generate_answer(args.query)
        print("\n" + "=" * 60)
        print("ANSWER:")
        print("=" * 60)
        print(result['answer'])
        print("\n" + "=" * 60)
        print("SOURCES:")
        print("=" * 60)
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['section']}")
    else:
        # Interactive mode
        rag.interactive_session()

    # Print stats
    print("\n" + "=" * 60)
    print("SESSION STATS:")
    print("=" * 60)
    stats = rag.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
