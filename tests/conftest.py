"""
pytest configuration and fixtures.
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Add paths for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/core/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


@pytest.fixture
def mock_vector_store():
    """Fixture providing a mocked vector store."""
    store = MagicMock()
    store.search.return_value = {
        "documents": [["doc1", "doc2"]],
        "metadatas": [[{"id": 1}, {"id": 2}]]
    }
    store.add_documents.return_value = None
    return store


@pytest.fixture
def temp_image(tmp_path):
    """Fixture providing a temporary image file."""
    img_path = tmp_path / "test_image.png"
    # Create a minimal valid PNG
    img_path.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)
    return str(img_path)


@pytest.fixture
def mock_api_responses():
    """Fixture providing mock API responses."""
    return {
        "opensea": {"collection": "test", "floor_price": 0.1},
        "etherscan": {"result": {"SafeGasPrice": "30"}},
        "gemini": {"text": "Generated content"}
    }


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Clean environment for each test."""
    # Remove sensitive keys to test fallback behavior
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENSEA_API_KEY", raising=False)
