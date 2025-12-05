"""
Demo script for RAG system with UTF-8 encoding.
"""

import sys
import io

# Force UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from scripts.rag_gitcommit_faiss import GitCommitRAG

def demo_queries():
    """Run demonstration queries."""
    print("\n" + "=" * 70)
    print(" GIT COMMIT CONVENTION RAG SYSTEM - DEMO")
    print("=" * 70)

    # Initialize RAG
    print("\nInitializing RAG system...")
    rag = GitCommitRAG(use_faiss=True, use_gpu=False)

    # Demo queries
    queries = [
        "How do I create a feature branch?",
        "What are the different commit types?",
        "How do I handle merge conflicts?",
        "What is the branch locking system?"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 70}")
        print(f"QUERY {i}: {query}")
        print("=" * 70)

        result = rag.generate_answer(query, n_results=2, use_genai=False)

        print("\nANSWER:")
        print("-" * 70)
        print(result['answer'][:400] + "..." if len(result['answer']) > 400 else result['answer'])

        print("\nSOURCES:")
        print("-" * 70)
        for j, source in enumerate(result['sources'], 1):
            score = source.get('score', 0)
            print(f"{j}. {source['section']} (relevance: {score:.3f})")

    # Stats
    print("\n" + "=" * 70)
    print("SESSION STATS")
    print("=" * 70)
    stats = rag.get_memory_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nThe RAG system is fully functional!")
    print("Try: python demo_rag.py --interactive for interactive mode")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        from scripts.rag_gitcommit_faiss import GitCommitRAG
        rag = GitCommitRAG(use_faiss=True, use_gpu=False)
        rag.interactive_session()
    else:
        demo_queries()
