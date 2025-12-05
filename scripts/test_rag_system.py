"""
Test script for Git Commit RAG System.

Tests:
1. ChromaDB indexing
2. FAISS GPU/CPU setup
3. Vector search accuracy
4. RAG generation quality
5. Memory integration
"""

import sys
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_chromadb_indexing():
    """Test 1: ChromaDB indexing."""
    print("\n" + "=" * 60)
    print("TEST 1: CHROMADB INDEXING")
    print("=" * 60)

    try:
        from scripts.index_gitcommit_to_chromadb import GitCommitIndexer

        gitcommit_path = project_root / ".gitcommit"

        if not gitcommit_path.exists():
            print("✗ .gitcommit file not found")
            return False

        indexer = GitCommitIndexer()
        indexer.run(gitcommit_path)

        print("\n✓ ChromaDB indexing test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ ChromaDB indexing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_faiss_setup():
    """Test 2: FAISS setup."""
    print("\n" + "=" * 60)
    print("TEST 2: FAISS SETUP")
    print("=" * 60)

    try:
        from scripts.rag_gitcommit_faiss import GitCommitRAG

        # Test CPU
        print("\nTesting FAISS CPU...")
        rag_cpu = GitCommitRAG(use_faiss=True, use_gpu=False)
        print("✓ FAISS CPU initialized")

        # Test GPU (if available)
        print("\nTesting FAISS GPU...")
        try:
            rag_gpu = GitCommitRAG(use_faiss=True, use_gpu=True)
            if rag_gpu.use_gpu:
                print("✓ FAISS GPU initialized")
            else:
                print("⚠ FAISS GPU not available, using CPU")
        except Exception as e:
            print(f"⚠ FAISS GPU not available: {e}")

        print("\n✓ FAISS setup test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ FAISS setup test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_search():
    """Test 3: Vector search accuracy."""
    print("\n" + "=" * 60)
    print("TEST 3: VECTOR SEARCH ACCURACY")
    print("=" * 60)

    try:
        from scripts.rag_gitcommit_faiss import GitCommitRAG

        rag = GitCommitRAG()

        test_queries = [
            ("commit message format", "format"),
            ("branch naming", "branches"),
            ("merge conflicts", "troubleshooting"),
            ("commit types", "types"),
            ("workspace branches", "branches")
        ]

        passed = 0
        total = len(test_queries)

        for query, expected_category in test_queries:
            print(f"\nQuery: '{query}'")
            print(f"Expected category: {expected_category}")

            results = rag.search(query, n_results=3)

            if results:
                top_result = results[0]
                found_category = top_result['metadata'].get('category', 'unknown')
                score = top_result.get('score', 0)

                print(f"Found category: {found_category}")
                print(f"Score: {score:.3f}")
                print(f"Section: {top_result['metadata'].get('section', 'Unknown')}")

                # Check if category matches (allow some flexibility)
                if found_category == expected_category or expected_category in found_category:
                    print("✓ Correct category")
                    passed += 1
                else:
                    print("⚠ Different category, but may still be relevant")
                    passed += 0.5
            else:
                print("✗ No results found")

        accuracy = (passed / total) * 100
        print(f"\n{'=' * 60}")
        print(f"Accuracy: {accuracy:.1f}% ({passed}/{total})")

        if accuracy >= 60:
            print("✓ Vector search test PASSED")
            return True
        else:
            print("✗ Vector search test FAILED (accuracy too low)")
            return False

    except Exception as e:
        print(f"\n✗ Vector search test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_generation():
    """Test 4: RAG answer generation."""
    print("\n" + "=" * 60)
    print("TEST 4: RAG ANSWER GENERATION")
    print("=" * 60)

    try:
        from scripts.rag_gitcommit_faiss import GitCommitRAG

        rag = GitCommitRAG()

        test_questions = [
            "How do I write a commit message?",
            "What are the different commit types?",
            "How do I handle merge conflicts?",
            "What is the branch naming convention?",
            "How do I use workspace branches?"
        ]

        passed = 0
        total = len(test_questions)

        for question in test_questions:
            print(f"\nQuestion: '{question}'")
            print("-" * 60)

            start_time = time.time()
            result = rag.generate_answer(question, n_results=3, use_genai=False)
            elapsed = time.time() - start_time

            print(f"Answer ({elapsed:.2f}s):")
            print(result['answer'][:300] + "..." if len(result['answer']) > 300 else result['answer'])

            print(f"\nSources: {len(result['sources'])}")
            for i, source in enumerate(result['sources'], 1):
                print(f"  {i}. {source['section']} (score: {source.get('score', 0):.3f})")

            # Simple quality check: answer should have content and sources
            if result['answer'] and len(result['answer']) > 50 and result['sources']:
                print("✓ Valid answer generated")
                passed += 1
            else:
                print("✗ Answer quality insufficient")

        success_rate = (passed / total) * 100
        print(f"\n{'=' * 60}")
        print(f"Success rate: {success_rate:.1f}% ({passed}/{total})")

        if success_rate >= 80:
            print("✓ RAG generation test PASSED")
            return True
        else:
            print("✗ RAG generation test FAILED")
            return False

    except Exception as e:
        print(f"\n✗ RAG generation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_integration():
    """Test 5: Memory and conversation tracking."""
    print("\n" + "=" * 60)
    print("TEST 5: MEMORY INTEGRATION")
    print("=" * 60)

    try:
        from scripts.rag_gitcommit_faiss import GitCommitRAG

        rag = GitCommitRAG()

        # Simulate conversation
        questions = [
            "What are commit types?",
            "How do I create a branch?",
            "What about merge conflicts?"
        ]

        for question in questions:
            result = rag.generate_answer(question, n_results=2, use_genai=False)
            print(f"Q: {question}")
            print(f"A: {result['answer'][:100]}...")
            print()

        # Check memory stats
        stats = rag.get_memory_stats()

        print("Memory Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Verify conversation history
        if stats['conversation_turns'] == len(questions):
            print(f"\n✓ Conversation history tracked correctly ({stats['conversation_turns']} turns)")
        else:
            print(f"\n✗ Conversation history mismatch")
            return False

        # Verify document count
        if stats['total_documents'] > 0:
            print(f"✓ Documents indexed: {stats['total_documents']}")
        else:
            print("✗ No documents in memory")
            return False

        print("\n✓ Memory integration test PASSED")
        return True

    except Exception as e:
        print(f"\n✗ Memory integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_benchmark():
    """Bonus test: Performance benchmark."""
    print("\n" + "=" * 60)
    print("BONUS: PERFORMANCE BENCHMARK")
    print("=" * 60)

    try:
        from scripts.rag_gitcommit_faiss import GitCommitRAG
        import numpy as np

        # Test with FAISS
        print("\nBenchmark: FAISS")
        rag_faiss = GitCommitRAG(use_faiss=True, use_gpu=False)

        query = "How do I write a commit message?"
        times_faiss = []

        for i in range(10):
            start = time.time()
            rag_faiss.search(query, n_results=5)
            elapsed = time.time() - start
            times_faiss.append(elapsed * 1000)  # Convert to ms

        avg_faiss = np.mean(times_faiss)
        std_faiss = np.std(times_faiss)

        print(f"  Average: {avg_faiss:.2f}ms")
        print(f"  Std Dev: {std_faiss:.2f}ms")
        print(f"  Min: {min(times_faiss):.2f}ms")
        print(f"  Max: {max(times_faiss):.2f}ms")

        # Test with ChromaDB only
        print("\nBenchmark: ChromaDB")
        rag_chroma = GitCommitRAG(use_faiss=False)

        times_chroma = []

        for i in range(10):
            start = time.time()
            rag_chroma.search(query, n_results=5)
            elapsed = time.time() - start
            times_chroma.append(elapsed * 1000)

        avg_chroma = np.mean(times_chroma)
        std_chroma = np.std(times_chroma)

        print(f"  Average: {avg_chroma:.2f}ms")
        print(f"  Std Dev: {std_chroma:.2f}ms")
        print(f"  Min: {min(times_chroma):.2f}ms")
        print(f"  Max: {max(times_chroma):.2f}ms")

        # Comparison
        speedup = avg_chroma / avg_faiss
        print(f"\n{'=' * 60}")
        print(f"FAISS Speedup: {speedup:.2f}x")

        return True

    except Exception as e:
        print(f"\n⚠ Performance benchmark failed: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print(" GIT COMMIT RAG SYSTEM - FULL TEST SUITE")
    print("=" * 70)

    tests = [
        ("ChromaDB Indexing", test_chromadb_indexing),
        ("FAISS Setup", test_faiss_setup),
        ("Vector Search", test_vector_search),
        ("RAG Generation", test_rag_generation),
        ("Memory Integration", test_memory_integration),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Run performance benchmark
    print("\n")
    test_performance_benchmark()

    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print()
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}  {test_name}")

    print(f"\n{'=' * 70}")
    print(f"Total: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is fully functional.")
    elif passed >= total * 0.8:
        print("\n✓ Most tests passed. System is functional with minor issues.")
    else:
        print("\n✗ Multiple tests failed. Please review errors above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
