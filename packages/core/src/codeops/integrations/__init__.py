"""
Espalha Integration Module

Complete integration of:
- FireCrawl (web scraping)
- LangGraph (orchestration)
- ComfyUI (asset generation)
- ComfyUIMCP (model control)
- ComfyUICLI (CLI execution)
- Anime4K (upscaling)
- CivitAI (model management)
- ChromaDB (vector storage)
- Neo4j (knowledge graph)
- Memory (persistent context)
"""

__version__ = "1.0.0"

from .pipeline import EspalhaIntegrationPipeline
from .firecrawl_client import FireCrawlClient
from .comfyui_client import ComfyUIClient
from .anime4k_client import Anime4KClient
from .civitai_client import CivitAIClient
from .chromadb_client import ChromaDBClient
from .neo4j_client import Neo4jClient
from .memory_client import MemoryClient
from .langgraph_builder import LangGraphBuilder

__all__ = [
    "EspalhaIntegrationPipeline",
    "FireCrawlClient",
    "ComfyUIClient",
    "Anime4KClient",
    "CivitAIClient",
    "ChromaDBClient",
    "Neo4jClient",
    "MemoryClient",
    "LangGraphBuilder",
]
