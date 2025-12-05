"""Test configuration and fixtures"""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Dict

import pytest

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def chromadb_client() -> AsyncGenerator:
    """Create ChromaDB test client"""
    client = chromadb.Client()
    yield client
    # Cleanup
    try:
        client.delete_collection("test_collection")
    except:
        pass


@pytest.fixture
async def neo4j_driver():
    """Create Neo4j test driver"""
    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=("neo4j", "password"),
        encrypted=False
    )
    yield driver
    driver.close()


@pytest.fixture
def mock_firecrawl_response() -> Dict[str, Any]:
    """Mock FireCrawl response"""
    return [
        {
            "keyword": "anime nft trending",
            "volume": 1500,
            "sentiment": 0.8,
            "source": "twitter",
            "url": "https://twitter.com/search"
        },
        {
            "keyword": "rare anime collectibles",
            "volume": 800,
            "sentiment": 0.75,
            "source": "reddit",
            "url": "https://reddit.com/r/NFT"
        }
    ]


@pytest.fixture
def mock_generated_asset() -> Dict[str, Any]:
    """Mock generated asset"""
    return {
        "id": "asset-test-001",
        "title": "Generated Anime NFT #001",
        "path": "/app/ComfyUI/output/asset_test_001.png",
        "model": "anything-v4.5",
        "style": "anime",
        "description": "High-quality anime character",
        "quality_score": 8.5,
        "embedding": [0.1] * 768,
        "model_id": "model-123"
    }


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock configuration"""
    return {
        "espalha_pipeline": {
            "firecrawl": {
                "enabled": True,
                "api_endpoint": "http://localhost:3000",
                "timeout": 30000
            },
            "comfyui": {
                "enabled": True,
                "api_endpoint": "http://localhost:8188",
                "mcp_enabled": True
            },
            "chromadb": {
                "enabled": True,
                "persist_directory": "./chroma_db"
            },
            "neo4j": {
                "enabled": True,
                "uri": "bolt://localhost:7687",
                "auth": ["neo4j", "password"]
            },
            "memory": {
                "enabled": True,
                "storage_dir": "./memory"
            }
        }
    }


@pytest.fixture
def temp_memory_dir(tmp_path) -> Path:
    """Create temporary memory directory"""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    return memory_dir


@pytest.fixture
def sample_memory_context() -> Dict[str, Any]:
    """Sample memory context"""
    return {
        "timestamp": "2025-12-05T10:30:00Z",
        "assets_generated": 5,
        "trends_processed": 10,
        "models_used": ["anything-v4.5"],
        "execution_time": 120.5
    }
