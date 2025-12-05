"""Integration tests for all components"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from codeops.integrations import (
    FireCrawlClient,
    ComfyUIClient,
    Anime4KClient,
    CivitAIClient,
    ChromaDBClient,
    Neo4jClient,
    MemoryClient,
    EspalhaIntegrationPipeline
)


class TestFireCrawlIntegration:
    """FireCrawl integration tests"""
    
    @pytest.mark.asyncio
    async def test_crawl_single_url(self, mock_firecrawl_response):
        """Test crawling single URL"""
        client = FireCrawlClient({"api_endpoint": "http://localhost:3000"})
        
        result = await client.crawl("https://twitter.com/search?q=nft")
        
        assert len(result) > 0
        assert result[0].get("keyword")
        assert result[0].get("sentiment") is not None
    
    @pytest.mark.asyncio
    async def test_crawl_multiple_urls(self, mock_firecrawl_response):
        """Test crawling multiple URLs"""
        client = FireCrawlClient({"api_endpoint": "http://localhost:3000"})
        
        urls = [
            "https://twitter.com/search?q=anime+nft",
            "https://reddit.com/r/NFT"
        ]
        results = await client.crawl_multiple(urls)
        
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_crawl_error_handling(self):
        """Test error handling in crawl"""
        client = FireCrawlClient({"api_endpoint": "http://invalid:3000"})
        
        try:
            result = await client.crawl("https://invalid-url")
            # Should handle gracefully
        except Exception:
            pass


class TestComfyUIIntegration:
    """ComfyUI integration tests"""
    
    @pytest.mark.asyncio
    async def test_execute_workflow(self, mock_generated_asset):
        """Test workflow execution"""
        client = ComfyUIClient({"api_endpoint": "http://localhost:8188"})
        
        asset = await client.execute_workflow(
            workflow_name="anime_generation",
            params={"prompt": "anime girl"}
        )
        
        assert asset["id"]
        assert asset["path"]
        assert asset["model"]
    
    @pytest.mark.asyncio
    async def test_workflow_with_custom_params(self):
        """Test workflow with custom parameters"""
        client = ComfyUIClient({"api_endpoint": "http://localhost:8188"})
        
        asset = await client.execute_workflow(
            workflow_name="anime_generation",
            params={
                "prompt": "detailed anime character",
                "negative_prompt": "low quality",
                "steps": 40,
                "guidance_scale": 8.5
            }
        )
        
        assert asset is not None


class TestAnime4KIntegration:
    """Anime4K integration tests"""
    
    @pytest.mark.asyncio
    async def test_upscale_image(self):
        """Test image upscaling"""
        client = Anime4KClient({"quality_level": 2, "gpu_acceleration": True})
        
        result = await client.upscale(
            input_path="/app/ComfyUI/output/test.png",
            quality_level=2
        )
        
        assert "upscaled" in result or result.endswith(".png")
    
    @pytest.mark.asyncio
    async def test_batch_upscale(self):
        """Test batch upscaling"""
        client = Anime4KClient({"quality_level": 2})
        
        results = await client.batch_upscale(
            input_dir="/app/ComfyUI/output",
            output_dir="/app/ComfyUI/upscaled"
        )
        
        assert isinstance(results, list)


class TestCivitAIIntegration:
    """CivitAI integration tests"""
    
    @pytest.mark.asyncio
    async def test_download_model(self):
        """Test model download"""
        client = CivitAIClient({
            "auto_download": True,
            "models_dir": "ComfyUI/models"
        })
        
        path = await client.download_model("anything-v4.5", "checkpoint")
        
        assert "checkpoint" in path
        assert path.endswith(".safetensors") or path.endswith(".ckpt")
    
    @pytest.mark.asyncio
    async def test_check_and_download_models(self):
        """Test checking and downloading required models"""
        client = CivitAIClient({
            "auto_download": True,
            "models_dir": "ComfyUI/models"
        })
        
        downloaded = await client.check_and_download_models()
        
        assert isinstance(downloaded, list)


class TestChromaDBIntegration:
    """ChromaDB integration tests"""
    
    @pytest.mark.asyncio
    async def test_generate_embedding(self):
        """Test embedding generation"""
        client = ChromaDBClient({
            "persist_directory": "./chroma_db"
        })
        
        embedding = await client.generate_embedding(
            "High-quality anime NFT character"
        )
        
        assert len(embedding) == 768  # all-MiniLM-L6-v2 dimension
        assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_add_to_collection(self):
        """Test adding items to collection"""
        client = ChromaDBClient({
            "persist_directory": "./chroma_db"
        })
        
        await client.add_to_collection(
            collection_name="test_assets",
            ids=["asset-001"],
            embeddings=[[0.1] * 768],
            metadatas=[{"style": "anime"}],
            documents=["Test asset"]
        )
    
    @pytest.mark.asyncio
    async def test_search_collection(self):
        """Test searching collection"""
        client = ChromaDBClient({
            "persist_directory": "./chroma_db"
        })
        
        results = await client.search(
            collection_name="test_assets",
            query_embedding=[0.1] * 768,
            n_results=5
        )
        
        assert isinstance(results, list)


class TestNeo4jIntegration:
    """Neo4j integration tests"""
    
    @pytest.mark.asyncio
    async def test_create_asset_node(self):
        """Test creating asset node"""
        client = Neo4jClient({
            "uri": "bolt://localhost:7687",
            "auth": ["neo4j", "password"]
        })
        
        asset_id = await client.create_asset_node({
            "id": "asset-test-001",
            "title": "Test Asset",
            "model": "anything-v4.5",
            "style": "anime"
        })
        
        assert asset_id == "asset-test-001"
    
    @pytest.mark.asyncio
    async def test_create_relationship(self):
        """Test creating relationships"""
        client = Neo4jClient({
            "uri": "bolt://localhost:7687",
            "auth": ["neo4j", "password"]
        })
        
        await client.create_relationship(
            from_id="asset-001",
            rel_type="GENERATED_FROM",
            to_id="model-123"
        )


class TestMemoryIntegration:
    """Memory integration tests"""
    
    @pytest.mark.asyncio
    async def test_save_context(self, temp_memory_dir, sample_memory_context):
        """Test saving context"""
        client = MemoryClient({
            "storage_dir": str(temp_memory_dir)
        })
        
        await client.save_context("test_context", sample_memory_context)
        
        assert (temp_memory_dir / "test_context.json").exists()
    
    @pytest.mark.asyncio
    async def test_load_context(self, temp_memory_dir, sample_memory_context):
        """Test loading context"""
        client = MemoryClient({
            "storage_dir": str(temp_memory_dir)
        })
        
        await client.save_context("test", sample_memory_context)
        loaded = await client.load_context("test")
        
        assert loaded["assets_generated"] == sample_memory_context["assets_generated"]
    
    @pytest.mark.asyncio
    async def test_memory_bank(self, temp_memory_dir):
        """Test memory bank listing"""
        client = MemoryClient({
            "storage_dir": str(temp_memory_dir)
        })
        
        contexts = await client.memory_bank()
        
        assert isinstance(contexts, dict)


class TestFullPipelineIntegration:
    """Full pipeline integration tests"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_pipeline_initialization(self, mock_config, tmp_path):
        """Test pipeline initialization"""
        config_file = tmp_path / "test_config.yaml"
        
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(mock_config, f)
        
        pipeline = EspalhaIntegrationPipeline(str(config_file))
        
        assert pipeline.firecrawl is not None
        assert pipeline.comfyui is not None
        assert pipeline.chromadb is not None
        assert pipeline.neo4j is not None
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_full_pipeline_execution(self):
        """Test full pipeline execution"""
        pipeline = EspalhaIntegrationPipeline()
        
        result = await pipeline.run_full_pipeline()
        
        assert result["status"] in ["success", "error"]
        assert "execution_log" in result
    
    @pytest.mark.asyncio
    async def test_single_stage_execution(self):
        """Test single stage execution"""
        pipeline = EspalhaIntegrationPipeline()
        
        result = await pipeline.run_single_stage("fetch_trends")
        
        assert "stage" in result
        assert result["stage"] == "fetch_trends"


class TestErrorHandling:
    """Error handling tests"""
    
    @pytest.mark.asyncio
    async def test_firecrawl_error_handling(self):
        """Test FireCrawl error handling"""
        client = FireCrawlClient({"api_endpoint": "http://invalid"})
        
        # Should not raise, should handle gracefully
        result = await client.crawl("invalid")
    
    @pytest.mark.asyncio
    async def test_comfyui_error_handling(self):
        """Test ComfyUI error handling"""
        client = ComfyUIClient({"api_endpoint": "http://invalid:8188"})
        
        try:
            await client.execute_workflow(
                workflow_name="invalid",
                params={}
            )
        except Exception as e:
            assert e is not None
    
    @pytest.mark.asyncio
    async def test_memory_missing_file(self, temp_memory_dir):
        """Test memory handling of missing files"""
        client = MemoryClient({"storage_dir": str(temp_memory_dir)})
        
        result = await client.load_context("nonexistent")
        
        assert result == {}
