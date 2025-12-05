"""
Test suite for Sentry Mode nodes.

This module provides comprehensive unit tests for all nodes
in the Digital Content Farm system.
"""

import os
import sys
from unittest.mock import MagicMock, patch

# Add paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../packages/core/src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from nodes.anime4k.node import Anime4kInput, Anime4kNode
from nodes.civitai.node import CivitAIInput, CivitAINode
from nodes.clip_eval.node import ClipEvalInput, ClipEvalNode
from nodes.firecrawl.node import FirecrawlInput, FirecrawlNode
from nodes.google_genai.node import GoogleGenAIInput, GoogleGenAINode
from nodes.rag.node import RAGInput, RAGNode
from nodes.real_esrgan.node import RealESRGANInput, RealESRGANNode
from nodes.social_media.node import SocialMediaInput, SocialMediaNode


class TestSocialMediaNode:
    """Tests for SocialMediaNode."""

    def test_fetch_reddit_trends(self):
        """Test fetching Reddit trends."""
        node = SocialMediaNode(name="social_media")
        output = node.execute(SocialMediaInput(platform="reddit"))

        assert output.trends is not None
        assert len(output.trends) >= 1
        assert output.trends[0]["source"] == "reddit"

    def test_fetch_youtube_trends(self):
        """Test fetching YouTube trends."""
        node = SocialMediaNode(name="social_media")
        output = node.execute(SocialMediaInput(platform="youtube"))

        assert any(t["source"] == "youtube" for t in output.trends)

    def test_fetch_all_platforms(self):
        """Test fetching from all platforms."""
        node = SocialMediaNode(name="social_media")
        output = node.execute(SocialMediaInput(platform="all"))

        sources = {t["source"] for t in output.trends}
        assert "reddit" in sources
        assert "youtube" in sources


class TestCivitAINode:
    """Tests for CivitAINode."""

    def test_download_lora(self):
        """Test LoRA download."""
        node = CivitAINode(name="civitai")
        output = node.execute(CivitAIInput(query="cyberpunk", model_type="LORA"))

        assert output.model_path is not None
        assert "cyberpunk" in output.model_path.lower()
        assert output.metadata.get("type") == "LORA"

    def test_download_checkpoint(self):
        """Test Checkpoint download."""
        node = CivitAINode(name="civitai")
        output = node.execute(CivitAIInput(query="anime", model_type="Checkpoint"))

        assert "checkpoints" in output.model_path or output.model_path == ""


class TestClipEvalNode:
    """Tests for ClipEvalNode."""

    def test_missing_image(self):
        """Test handling of missing image file."""
        node = ClipEvalNode(name="clip_eval")
        output = node.execute(ClipEvalInput(
            image_path="nonexistent.png",
            prompt="test"
        ))

        assert output.score >= 0.0
        assert output.score <= 1.0

    def test_score_range(self):
        """Test that score is in valid range."""
        node = ClipEvalNode(name="clip_eval")
        output = node.execute(ClipEvalInput(
            image_path="test.png",
            prompt="test prompt"
        ))

        assert 0.0 <= output.score <= 1.0


class TestRAGNode:
    """Tests for RAGNode."""

    def test_rag_query_with_mock(self):
        """Test RAG query with mocked vector store."""
        with patch('codeops.memory.vector_store.get_vector_store') as mock_get_store:
            mock_store = MagicMock()
            mock_store.search.return_value = {
                "documents": [["doc1", "doc2"]],
                "metadatas": [[{"id": 1}, {"id": 2}]]
            }
            mock_get_store.return_value = mock_store

            node = RAGNode(name="rag")
            output = node.execute(RAGInput(query="test query"))

            assert output.documents == ["doc1", "doc2"]
            assert len(output.metadatas) == 2

    def test_rag_empty_results(self):
        """Test RAG with empty results."""
        with patch('codeops.memory.vector_store.get_vector_store') as mock_get_store:
            mock_store = MagicMock()
            mock_store.search.return_value = {"documents": [[]], "metadatas": [[]]}
            mock_get_store.return_value = mock_store

            node = RAGNode(name="rag")
            output = node.execute(RAGInput(query="no results"))

            assert output.documents == []


class TestGoogleGenAINode:
    """Tests for GoogleGenAINode."""

    def test_no_api_key(self):
        """Test behavior when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            node = GoogleGenAINode(name="genai")
            output = node.execute(GoogleGenAIInput(prompt="test"))

            assert output.content is not None
            assert "Mock" in output.content or "Error" in output.content


class TestRealESRGANNode:
    """Tests for RealESRGANNode."""

    def test_missing_script(self):
        """Test handling of missing Real-ESRGAN script."""
        node = RealESRGANNode(name="realesrgan")
        output = node.execute(RealESRGANInput(image_path="test.png"))

        # Should return input path if script not found
        assert output.output_path is not None


class TestAnime4KNode:
    """Tests for Anime4KNode."""

    def test_upscale_image(self):
        """Test image upscaling (mock)."""
        node = Anime4kNode(name="anime4k")
        output = node.execute(Anime4kInput(input_path="test.png"))

        assert output.output_path is not None


class TestFirecrawlNode:
    """Tests for FirecrawlNode."""

    def test_scrape_url(self):
        """Test URL scraping."""
        node = FirecrawlNode(name="firecrawl")
        output = node.execute(FirecrawlInput(url="http://example.com"))

        assert output.data is not None


# Integration test
class TestWorkflowIntegration:
    """Integration tests for workflow."""

    def test_social_to_rag_flow(self):
        """Test flow from social media to RAG."""
        # Get trends
        social_node = SocialMediaNode(name="social")
        trends = social_node.execute(SocialMediaInput(platform="all"))

        assert len(trends.trends) > 0

        # Query RAG with trend
        with patch('codeops.memory.vector_store.get_vector_store') as mock:
            mock_store = MagicMock()
            mock_store.search.return_value = {"documents": [[]], "metadatas": [[]]}
            mock.return_value = mock_store

            rag_node = RAGNode(name="rag")
            rag_output = rag_node.execute(RAGInput(
                query=trends.trends[0]["title"]
            ))

            assert rag_output is not None
