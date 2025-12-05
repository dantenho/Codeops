"""
Windows-compatible RAG test runner with UTF-8 encoding.
"""

import sys
import io

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Now import and run tests
from scripts.test_rag_system import run_all_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
