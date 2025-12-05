"""
Espalha Integration Pipeline

Complete orchestration of all tools for NFT asset generation
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

import yaml
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from .firecrawl_client import FireCrawlClient
from .comfyui_client import ComfyUIClient
from .anime4k_client import Anime4KClient
from .civitai_client import CivitAIClient
from .chromadb_client import ChromaDBClient
from .neo4j_client import Neo4jClient
from .memory_client import MemoryClient

logger = logging.getLogger(__name__)


class PipelineState(TypedDict):
    """State management for the pipeline"""
    market_trends: List[Dict[str, Any]]
    generated_assets: List[Dict[str, Any]]
    embeddings: List[List[float]]
    graph_relationships: Dict[str, Any]
    memory_context: Dict[str, Any]
    execution_log: List[str]


class EspalhaIntegrationPipeline:
    """
    Complete integration pipeline for NFT asset generation.
    
    Workflow:
    1. FireCrawl: Scrape market trends
    2. LangGraph: Analyze and decide
    3. ComfyUI: Generate assets
    4. Anime4K: Upscale
    5. ChromaDB: Index embeddings
    6. Neo4j: Update knowledge graph
    7. Memory: Save context
    """
    
    def __init__(self, config_path: str = "config/espalha.yaml"):
        """Initialize pipeline with configuration"""
        self.config = self._load_config(config_path)
        
        # Initialize clients
        self.firecrawl = FireCrawlClient(self.config.get("firecrawl", {}))
        self.comfyui = ComfyUIClient(self.config.get("comfyui", {}))
        self.anime4k = Anime4KClient(self.config.get("anime4k", {}))
        self.civitai = CivitAIClient(self.config.get("civitai", {}))
        self.chromadb = ChromaDBClient(self.config.get("chromadb", {}))
        self.neo4j = Neo4jClient(self.config.get("neo4j", {}))
        self.memory = MemoryClient(self.config.get("memory", {}))
        
        # Initialize LangGraph
        self.graph = self._build_workflow()
        self.compiled_graph = self.graph.compile()
        
        logger.info("✅ EspalhaIntegrationPipeline initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config.get("espalha_pipeline", {})
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(PipelineState)
        
        # Add nodes
        workflow.add_node("fetch_trends", self._fetch_trends)
        workflow.add_node("generate_strategy", self._generate_strategy)
        workflow.add_node("generate_assets", self._generate_assets)
        workflow.add_node("upscale_assets", self._upscale_assets)
        workflow.add_node("index_vector_db", self._index_vector_db)
        workflow.add_node("update_graph", self._update_graph)
        workflow.add_node("save_memory", self._save_memory)
        
        # Add edges
        workflow.add_edge("fetch_trends", "generate_strategy")
        workflow.add_edge("generate_strategy", "generate_assets")
        workflow.add_edge("generate_assets", "upscale_assets")
        workflow.add_edge("upscale_assets", "index_vector_db")
        workflow.add_edge("index_vector_db", "update_graph")
        workflow.add_edge("update_graph", "save_memory")
        workflow.add_edge("save_memory", END)
        
        # Set entry point
        workflow.set_entry_point("fetch_trends")
        
        return workflow
    
    async def _fetch_trends(self, state: PipelineState) -> PipelineState:
        """Stage 1: FireCrawl - Fetch market trends"""
        logger.info("🌐 [Stage 1] Fetching market trends with FireCrawl...")
        state["execution_log"].append("Started: fetch_trends")
        
        try:
            # Scrape multiple platforms
            trends = await self.firecrawl.crawl_multiple([
                "https://twitter.com/search?q=anime+nft",
                "https://reddit.com/r/NFT",
                "https://opensea.io/rankings",
            ])
            
            state["market_trends"] = trends
            state["execution_log"].append(f"Fetched {len(trends)} trends")
            logger.info(f"✅ Fetched {len(trends)} trends")
            
        except Exception as e:
            logger.error(f"❌ FireCrawl error: {e}")
            state["execution_log"].append(f"Error in fetch_trends: {str(e)}")
        
        return state
    
    async def _generate_strategy(self, state: PipelineState) -> PipelineState:
        """Stage 2: LangGraph - Generate strategy"""
        logger.info("📊 [Stage 2] Analyzing trends and generating strategy...")
        state["execution_log"].append("Started: generate_strategy")
        
        try:
            # Use LangGraph to analyze trends
            strategy = await self._analyze_with_langgraph(state["market_trends"])
            
            state["memory_context"]["strategy"] = strategy
            state["execution_log"].append("Strategy generated")
            logger.info("✅ Strategy generated")
            
        except Exception as e:
            logger.error(f"❌ Strategy generation error: {e}")
            state["execution_log"].append(f"Error in generate_strategy: {str(e)}")
        
        return state
    
    async def _generate_assets(self, state: PipelineState) -> PipelineState:
        """Stage 3: ComfyUI - Generate assets"""
        logger.info("🎨 [Stage 3] Generating assets with ComfyUI...")
        state["execution_log"].append("Started: generate_assets")
        
        try:
            generated_assets = []
            
            for trend in state["market_trends"][:5]:  # Limit to 5 for demo
                # Download latest models if needed
                await self.civitai.check_and_download_models()
                
                # Execute ComfyUI workflow
                asset = await self.comfyui.execute_workflow(
                    workflow_name="anime_generation",
                    params={
                        "prompt": trend.get("keyword"),
                        "negative_prompt": "low quality, blurry",
                        "steps": 30,
                        "guidance_scale": 7.5
                    }
                )
                
                generated_assets.append(asset)
            
            state["generated_assets"] = generated_assets
            state["execution_log"].append(f"Generated {len(generated_assets)} assets")
            logger.info(f"✅ Generated {len(generated_assets)} assets")
            
        except Exception as e:
            logger.error(f"❌ Asset generation error: {e}")
            state["execution_log"].append(f"Error in generate_assets: {str(e)}")
        
        return state
    
    async def _upscale_assets(self, state: PipelineState) -> PipelineState:
        """Stage 4: Anime4K - Upscale assets"""
        logger.info("🎬 [Stage 4] Upscaling with Anime4K...")
        state["execution_log"].append("Started: upscale_assets")
        
        try:
            upscaled = []
            
            for asset in state["generated_assets"]:
                upscaled_path = await self.anime4k.upscale(
                    input_path=asset["path"],
                    quality_level=2
                )
                
                asset["upscaled_path"] = upscaled_path
                upscaled.append(asset)
            
            state["generated_assets"] = upscaled
            state["execution_log"].append(f"Upscaled {len(upscaled)} assets")
            logger.info(f"✅ Upscaled {len(upscaled)} assets")
            
        except Exception as e:
            logger.error(f"❌ Upscaling error: {e}")
            state["execution_log"].append(f"Error in upscale_assets: {str(e)}")
        
        return state
    
    async def _index_vector_db(self, state: PipelineState) -> PipelineState:
        """Stage 5: ChromaDB - Index embeddings"""
        logger.info("📊 [Stage 5] Indexing embeddings in ChromaDB...")
        state["execution_log"].append("Started: index_vector_db")
        
        try:
            indexed = 0
            
            for asset in state["generated_assets"]:
                # Generate embedding
                embedding = await self.chromadb.generate_embedding(
                    asset["description"]
                )
                
                # Add to collection
                await self.chromadb.add_to_collection(
                    collection_name="generated_assets",
                    ids=[asset["id"]],
                    embeddings=[embedding],
                    metadatas=[{
                        "model": asset.get("model"),
                        "style": asset.get("style"),
                        "quality_score": asset.get("quality_score", 8.0)
                    }],
                    documents=[asset["description"]]
                )
                
                indexed += 1
            
            state["embeddings"] = [asset.get("embedding") for asset in state["generated_assets"]]
            state["execution_log"].append(f"Indexed {indexed} assets in ChromaDB")
            logger.info(f"✅ Indexed {indexed} assets")
            
        except Exception as e:
            logger.error(f"❌ ChromaDB indexing error: {e}")
            state["execution_log"].append(f"Error in index_vector_db: {str(e)}")
        
        return state
    
    async def _update_graph(self, state: PipelineState) -> PipelineState:
        """Stage 6: Neo4j - Update knowledge graph"""
        logger.info("🌐 [Stage 6] Updating Neo4j knowledge graph...")
        state["execution_log"].append("Started: update_graph")
        
        try:
            created_nodes = 0
            
            for asset in state["generated_assets"]:
                # Create asset node
                await self.neo4j.create_asset_node({
                    "id": asset["id"],
                    "title": asset["title"],
                    "model": asset.get("model"),
                    "style": asset.get("style"),
                    "created_at": datetime.now().isoformat()
                })
                
                # Create relationships
                if "model_id" in asset:
                    await self.neo4j.create_relationship(
                        asset["id"],
                        "GENERATED_FROM",
                        asset["model_id"]
                    )
                
                created_nodes += 1
            
            state["graph_relationships"]["nodes_created"] = created_nodes
            state["execution_log"].append(f"Created {created_nodes} graph nodes")
            logger.info(f"✅ Created {created_nodes} graph nodes")
            
        except Exception as e:
            logger.error(f"❌ Neo4j update error: {e}")
            state["execution_log"].append(f"Error in update_graph: {str(e)}")
        
        return state
    
    async def _save_memory(self, state: PipelineState) -> PipelineState:
        """Stage 7: Memory - Save execution context"""
        logger.info("💾 [Stage 7] Saving execution context...")
        state["execution_log"].append("Started: save_memory")
        
        try:
            memory_data = {
                "timestamp": datetime.now().isoformat(),
                "assets_generated": len(state["generated_assets"]),
                "trends_processed": len(state["market_trends"]),
                "execution_log": state["execution_log"],
                "metadata": {
                    "model": state.get("memory_context", {}).get("strategy"),
                    "upscale_quality": 2
                }
            }
            
            await self.memory.save_context(
                key=f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                context=memory_data
            )
            
            state["execution_log"].append("Context saved to memory")
            logger.info("✅ Context saved")
            
        except Exception as e:
            logger.error(f"❌ Memory save error: {e}")
            state["execution_log"].append(f"Error in save_memory: {str(e)}")
        
        return state
    
    async def _analyze_with_langgraph(self, trends: List[Dict]) -> Dict[str, Any]:
        """Analyze trends using LangGraph"""
        # TODO: Implement LangGraph analysis
        return {
            "top_keywords": [t.get("keyword") for t in trends[:3]],
            "sentiment": "positive",
            "recommendation": "Generate anime style NFTs"
        }
    
    async def run_full_pipeline(self) -> Dict[str, Any]:
        """Execute complete pipeline"""
        logger.info("🚀 Starting Espalha Integration Pipeline...")
        
        initial_state: PipelineState = {
            "market_trends": [],
            "generated_assets": [],
            "embeddings": [],
            "graph_relationships": {},
            "memory_context": {},
            "execution_log": ["Pipeline started"]
        }
        
        try:
            # Execute pipeline
            final_state = await self.compiled_graph.ainvoke(initial_state)
            
            logger.info("✅ Pipeline completed successfully!")
            
            return {
                "status": "success",
                "assets_generated": len(final_state["generated_assets"]),
                "trends_processed": len(final_state["market_trends"]),
                "execution_log": final_state["execution_log"]
            }
            
        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "execution_log": initial_state["execution_log"]
            }
    
    async def run_single_stage(self, stage_name: str) -> Dict[str, Any]:
        """Run a single stage for testing"""
        stage_map = {
            "fetch_trends": self._fetch_trends,
            "generate_strategy": self._generate_strategy,
            "generate_assets": self._generate_assets,
            "upscale_assets": self._upscale_assets,
            "index_vector_db": self._index_vector_db,
            "update_graph": self._update_graph,
            "save_memory": self._save_memory,
        }
        
        if stage_name not in stage_map:
            return {"error": f"Unknown stage: {stage_name}"}
        
        state: PipelineState = {
            "market_trends": [],
            "generated_assets": [],
            "embeddings": [],
            "graph_relationships": {},
            "memory_context": {},
            "execution_log": [f"Running stage: {stage_name}"]
        }
        
        try:
            result_state = await stage_map[stage_name](state)
            return {"status": "success", "stage": stage_name, "result": result_state}
        except Exception as e:
            return {"status": "error", "stage": stage_name, "error": str(e)}


# Entry point
if __name__ == "__main__":
    async def main():
        pipeline = EspalhaIntegrationPipeline()
        result = await pipeline.run_full_pipeline()
        print(result)
    
    asyncio.run(main())
