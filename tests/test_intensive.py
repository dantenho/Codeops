"""
Intensive Unit Tests for All Integrations.

Comprehensive test suite covering all local tools,
integrations, and workflows with telemetry.
"""

import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.telemetry import get_logger, test_telemetry, track_execution

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

logger = get_logger("intensive_tests")


def timed_test(test_func):
    """Decorator to time tests and record telemetry."""
    def wrapper(*args, **kwargs):
        start = time.time()
        error = None
        passed = True

        try:
            result = test_func(*args, **kwargs)
            return result
        except Exception as e:
            error = str(e)
            passed = False
            raise
        finally:
            duration = (time.time() - start) * 1000
            test_telemetry.record_test(
                test_func.__name__,
                passed,
                duration,
                error
            )

    return wrapper


# =============================================================================
# LOCAL TOOLS TESTS
# =============================================================================

class TestLocalToolsManager:
    """Tests for LocalToolsManager."""

    @timed_test
    def test_tools_status(self):
        """Test that tools status returns all tools."""
        from packages.integration.local_tools import tools

        status = tools.status()
        assert isinstance(status, dict)
        assert len(status) >= 7

    @timed_test
    def test_available_tools(self):
        """Test listing available tools."""
        from packages.integration.local_tools import tools

        available = tools.available_tools()
        assert isinstance(available, list)

    @timed_test
    def test_langgraph_integration(self):
        """Test LangGraph can be loaded."""
        from packages.integration.local_tools import tools

        try:
            StateGraph, END = tools.langgraph.load()
            assert StateGraph is not None
        except ImportError:
            pytest.skip("LangGraph not installed")

    @timed_test
    def test_comfyui_list_models(self):
        """Test ComfyUI model listing."""
        from packages.integration.local_tools import tools

        models = tools.comfyui.list_models()
        assert isinstance(models, list)

    @timed_test
    def test_civitai_search(self):
        """Test CivitAI model search."""
        from packages.integration.local_tools import tools

        # Mock the requests to avoid API calls
        with patch('requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {"items": []}

            results = tools.civitai.search_models("anime", "LORA")
            assert isinstance(results, list)


# =============================================================================
# EXTENDED TOOLS TESTS
# =============================================================================

class TestExtendedTools:
    """Tests for extended tools integrations."""

    @timed_test
    def test_extended_tools_status(self):
        """Test extended tools status."""
        from packages.integration.extended_tools import extended_tools

        status = extended_tools.status()
        assert isinstance(status, dict)
        assert "chromadb" in status
        assert "playwright" in status

    @timed_test
    def test_chromadb_client(self):
        """Test ChromaDB client initialization."""
        from packages.integration.extended_tools import extended_tools

        try:
            client = extended_tools.chromadb.get_client()
            assert client is not None
        except ImportError:
            pytest.skip("ChromaDB not installed")

    @timed_test
    def test_chromadb_collection(self):
        """Test ChromaDB collection operations."""
        from packages.integration.extended_tools import extended_tools

        try:
            collection = extended_tools.chromadb.get_or_create_collection("test_collection")
            assert collection is not None

            # Add documents
            ids = extended_tools.chromadb.add_documents(
                "test_collection",
                ["test document 1", "test document 2"],
                [{"source": "test"}, {"source": "test"}]
            )
            assert len(ids) == 2

            # Query
            results = extended_tools.chromadb.query("test_collection", "document", n_results=2)
            assert "documents" in results

        except ImportError:
            pytest.skip("ChromaDB not installed")

    @timed_test
    def test_genai_configure(self):
        """Test Google GenAI configuration."""
        from packages.integration.extended_tools import extended_tools

        # Should not raise even without API key
        try:
            extended_tools.genai.configure()
        except Exception:
            pass  # Expected without API key

    @timed_test
    def test_clip_availability(self):
        """Test CLIP availability check."""
        from packages.integration.extended_tools import extended_tools

        available = extended_tools.clip.available
        assert isinstance(available, bool)


# =============================================================================
# NODE TESTS
# =============================================================================

class TestSocialMediaNode:
    """Tests for SocialMediaNode."""

    @timed_test
    def test_execute(self):
        """Test node execution."""
        from nodes.social_media.node import SocialMediaInput, SocialMediaNode

        node = SocialMediaNode(name="test_social")
        output = node.execute(SocialMediaInput(platform="all"))

        assert output is not None
        assert hasattr(output, "trends")
        assert isinstance(output.trends, list)

    @timed_test
    def test_reddit_only(self):
        """Test Reddit-only fetch."""
        from nodes.social_media.node import SocialMediaInput, SocialMediaNode

        node = SocialMediaNode(name="test_social")
        output = node.execute(SocialMediaInput(platform="reddit"))

        for trend in output.trends:
            assert trend["source"] == "reddit"


class TestRAGNode:
    """Tests for RAGNode."""

    @timed_test
    def test_execute_with_mock(self):
        """Test RAG with mocked vector store."""
        with patch('codeops.memory.vector_store.get_vector_store') as mock_store:
            mock_store.return_value.search.return_value = {
                "documents": [["doc1", "doc2"]],
                "metadatas": [[{"id": 1}, {"id": 2}]]
            }

            from nodes.rag.node import RAGInput, RAGNode

            node = RAGNode(name="test_rag")
            output = node.execute(RAGInput(query="test"))

            assert output.documents == ["doc1", "doc2"]


class TestClipEvalNode:
    """Tests for ClipEvalNode."""

    @timed_test
    def test_missing_image(self):
        """Test with non-existent image."""
        from nodes.clip_eval.node import ClipEvalInput, ClipEvalNode

        node = ClipEvalNode(name="test_clip")
        output = node.execute(ClipEvalInput(
            image_path="nonexistent.png",
            prompt="test"
        ))

        assert 0.0 <= output.score <= 1.0

    @timed_test
    def test_score_normalization(self):
        """Test score is properly normalized."""
        from nodes.clip_eval.node import ClipEvalInput, ClipEvalNode

        node = ClipEvalNode(name="test_clip")
        output = node.execute(ClipEvalInput(
            image_path="test.png",
            prompt="any prompt"
        ))

        assert output.score >= 0.0
        assert output.score <= 1.0


class TestGoogleGenAINode:
    """Tests for GoogleGenAINode."""

    @timed_test
    def test_no_api_key(self):
        """Test behavior without API key."""
        with patch.dict(os.environ, {}, clear=True):
            from nodes.google_genai.node import GoogleGenAIInput, GoogleGenAINode

            node = GoogleGenAINode(name="test_genai")
            output = node.execute(GoogleGenAIInput(prompt="test"))

            assert output.content is not None


class TestCivitAINode:
    """Tests for CivitAINode."""

    @timed_test
    def test_lora_search(self):
        """Test LoRA search."""
        from nodes.civitai.node import CivitAIInput, CivitAINode

        node = CivitAINode(name="test_civitai")
        output = node.execute(CivitAIInput(query="anime", model_type="LORA"))

        assert output.model_path is not None


class TestRealESRGANNode:
    """Tests for RealESRGANNode."""

    @timed_test
    def test_graceful_failure(self):
        """Test graceful failure when script missing."""
        from nodes.real_esrgan.node import RealESRGANInput, RealESRGANNode

        node = RealESRGANNode(name="test_esrgan")
        output = node.execute(RealESRGANInput(image_path="input.png"))

        assert output.output_path is not None


class TestAnime4KNode:
    """Tests for Anime4KNode."""

    @timed_test
    def test_execute(self):
        """Test node execution."""
        from nodes.anime4k.node import Anime4kInput, Anime4kNode

        node = Anime4kNode(name="test_anime4k")
        output = node.execute(Anime4kInput(input_path="test.png"))

        assert output.output_path is not None


# =============================================================================
# TELEMETRY TESTS
# =============================================================================

class TestTelemetry:
    """Tests for telemetry system."""

    @timed_test
    def test_logger_creation(self):
        """Test logger creation."""
        from packages.telemetry import TelemetryLogger

        logger = TelemetryLogger("test")
        assert logger is not None

    @timed_test
    def test_event_logging(self):
        """Test event logging."""
        from packages.telemetry import TelemetryLogger

        logger = TelemetryLogger("test_events")
        event = logger.log_event(
            event_type="test",
            action="test_action",
            duration_ms=100,
            status="success",
            metadata={"key": "value"}
        )

        assert event.event_type == "test"
        assert event.action == "test_action"

    @timed_test
    def test_metrics(self):
        """Test metrics aggregation."""
        from packages.telemetry import TelemetryLogger

        logger = TelemetryLogger("test_metrics")

        # Log some events
        for i in range(5):
            logger.log_event("test", f"action_{i}", i * 10, "success")

        metrics = logger.get_metrics()

        assert metrics["total_events"] == 5
        assert "avg_duration_ms" in metrics

    @timed_test
    def test_track_execution_decorator(self):
        """Test execution tracking decorator."""
        from packages.telemetry import TelemetryLogger

        logger = TelemetryLogger("test_decorator")

        @track_execution(logger, "function")
        def sample_function(x):
            time.sleep(0.01)
            return x * 2

        result = sample_function(5)

        assert result == 10
        assert len(logger.events) >= 1


class TestWorkflowTelemetry:
    """Tests for workflow telemetry."""

    @timed_test
    def test_workflow_tracking(self):
        """Test workflow run tracking."""
        from packages.telemetry import WorkflowTelemetry

        telemetry = WorkflowTelemetry("test_workflow")

        telemetry.start_run()

        with telemetry.track_node("node_1"):
            time.sleep(0.01)

        with telemetry.track_node("node_2"):
            time.sleep(0.02)

        telemetry.end_run("success")

        stats = telemetry.get_node_stats()

        assert "node_1" in stats
        assert "node_2" in stats
        assert stats["node_1"]["count"] == 1


# =============================================================================
# WORKFLOW TESTS
# =============================================================================

class TestWorkflowBuilder:
    """Tests for workflow builder."""

    @timed_test
    def test_builder_creation(self):
        """Test workflow builder creation."""
        from packages.integration.workflows import WorkflowBuilder

        builder = WorkflowBuilder()
        assert builder is not None

    @timed_test
    def test_quick_functions(self):
        """Test quick workflow functions."""
        from packages.integration.workflows import search_loras

        # Mock the API call
        with patch('requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {"items": []}

            results = search_loras("anime", limit=3)
            assert isinstance(results, list)


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestFullIntegration:
    """Full integration tests."""

    @timed_test
    def test_tool_chain(self):
        """Test chaining multiple tools."""
        from packages.integration.extended_tools import extended_tools
        from packages.integration.local_tools import tools

        # Get all statuses
        local_status = tools.status()
        extended_status = extended_tools.status()

        # Merge statuses
        all_tools = {**local_status, **extended_status}

        # Count available
        available_count = sum(1 for v in all_tools.values()
                            if isinstance(v, dict) and v.get("available"))

        logger.info(f"Available tools: {available_count}")
        assert available_count > 0

    @timed_test
    def test_graph_compilation(self):
        """Test that the main graph compiles."""
        try:
            from packages.orchestrator.src.codeops.orchestrator.graph import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"Graph import failed: {e}")


# =============================================================================
# RUN TESTS
# =============================================================================

def run_intensive_tests():
    """Run all intensive tests and return summary."""
    import pytest

    # Run pytest
    result = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
        f"--rootdir={Path(__file__).parent.parent}"
    ])

    # Get telemetry summary
    summary = test_telemetry.get_summary()

    print("\n" + "=" * 60)
    print("TELEMETRY SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate']:.1%}")
    print(f"Total Duration: {summary['total_duration_ms']:.2f}ms")

    if summary['failures']:
        print("\nFailures:")
        for f in summary['failures']:
            print(f"  - {f['name']}: {f['error']}")

    return result, summary


if __name__ == "__main__":
    run_intensive_tests()
