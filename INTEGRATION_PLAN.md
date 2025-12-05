# Complete Integration Plan - FireCrawl, LangGraph, ComfyUI & Databases

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Input Layer (FireCrawl)                     │
│            Web scraping → Data Collection → Processing           │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Orchestration Layer                           │
│  LangGraph (Agent Workflow) + ComfyUIMCP + ComfyUICLI           │
│         Asset Generation Pipeline Management                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  Generation Layer                               │
│  ComfyUI Workflows:                                             │
│  ├─ Image Generation (Stable Diffusion + LoRAs)               │
│  ├─ Quality Enhancement (Anime4K Upscaling)                   │
│  └─ Model Management (CivitAI Downloads)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  Vector/Graph Storage Layer                      │
│  ├─ ChromaDB: Embeddings + Semantic Search                      │
│  ├─ Neo4j: Relationships + Knowledge Graph                      │
│  └─ Memory: Persistent State + Context                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Output Layer                                  │
│  NFT Minting → Blockchain Publishing → Live Display             │
└─────────────────────────────────────────────────────────────────┘
```

## Phase 1: Tool Installation & Configuration

### 1.1 FireCrawl (Web Scraping)
**Purpose**: Scrape market trends, social media, competitor data

**Installation**:
```bash
# Install locally
git clone https://github.com/mendableai/firecrawl.git
cd firecrawl
pip install -e .

# Docker option
docker run -d \
  -p 3000:3000 \
  -e API_KEY=your-key \
  mendableai/firecrawl:latest
```

**Configuration**:
```yaml
firecrawl:
  api_endpoint: "http://localhost:3000"
  timeout: 30000  # ms
  retries: 3
  
  crawlers:
    twitter:
      url: "https://twitter.com/search"
      selector: "tweet-content"
      depth: 2
    
    reddit:
      url: "https://reddit.com/r/NFT"
      selector: "post-content"
      depth: 2
    
    youtube:
      url: "https://youtube.com/results"
      selector: "video-title"
      depth: 1
```

### 1.2 LangGraph (Orchestration)
**Purpose**: Manage agent workflows and decision trees

**Installation**:
```bash
pip install langgraph langchain langchain-community
```

**Graph Definition**:
```python
from langgraph.graph import StateGraph
from typing import TypedDict

class PipelineState(TypedDict):
    market_trends: list
    generated_assets: list
    embeddings: list
    graph_relationships: dict
    memory_context: str

# Define workflow graph
workflow = StateGraph(PipelineState)
workflow.add_node("fetch_trends", fetch_trends_node)
workflow.add_node("generate_strategy", generate_strategy_node)
workflow.add_node("generate_assets", generate_assets_node)
workflow.add_node("index_vector_db", index_vector_db_node)
workflow.add_node("update_graph", update_graph_node)
workflow.add_node("save_memory", save_memory_node)

# Define edges
workflow.add_edge("fetch_trends", "generate_strategy")
workflow.add_edge("generate_strategy", "generate_assets")
workflow.add_edge("generate_assets", "index_vector_db")
workflow.add_edge("index_vector_db", "update_graph")
workflow.add_edge("update_graph", "save_memory")
```

### 1.3 ComfyUI (Local Installation)
**Purpose**: Image generation and processing

**Installation**:
```bash
# Download ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Install dependencies
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt

# Download models (Stable Diffusion)
# - checkpoints/
# - vae/
# - loras/  (from CivitAI)
```

**Directory Structure**:
```
ComfyUI/
├── web/
├── nodes/
├── models/
│   ├── checkpoints/          # SD 1.5, SDXL, etc.
│   ├── vae/                  # VAE models
│   ├── loras/                # LoRA models (anime, style-specific)
│   ├── embeddings/           # Textual inversion embeddings
│   └── animatediff/          # Animation models
├── input/                    # Input images
├── output/                   # Generated images
└── custom_nodes/
    ├── ComfyUI-AnimateDiff/
    ├── ComfyUI-Manager/
    └── custom-espalha/       # Custom nodes for pipeline
```

### 1.4 ComfyUIMCP (Model Control Protocol)
**Purpose**: Standardized ComfyUI workflow management

**Installation**:
```bash
pip install comfyui-mcp
```

**Configuration**:
```json
{
  "mcp_server": {
    "host": "localhost",
    "port": 5000,
    "api_key": "your-mcp-key"
  },
  "workflow_templates": {
    "anime_generation": {
      "checkpoint": "anything-v4.5-pruned",
      "lora": ["anime-style", "detailed-hands"],
      "sampling_steps": 30,
      "guidance_scale": 7.5
    },
    "upscaling": {
      "upscaler": "Real-ESRGAN",
      "scale": 4
    }
  }
}
```

### 1.5 ComfyUICLI (Command Line Interface)
**Purpose**: Headless workflow execution

**Installation**:
```bash
pip install comfyui-cli
```

**Usage**:
```bash
comfyui-cli run workflow.json \
  --input images/ \
  --output results/ \
  --gpu-device 0 \
  --batch-size 4
```

### 1.6 Anime4K (Upscaling)
**Purpose**: Enhance anime-style image quality

**Installation**:
```bash
# C++ implementation (faster)
git clone https://github.com/bloc97/Anime4KCPP.git
cd Anime4KCPP
mkdir build && cd build
cmake ..
make

# Or Python wrapper
pip install anime4kcpp

# Integration with ComfyUI
git clone https://github.com/bloc97/Anime4K-ComfyUI-node.git
cp -r Anime4K-ComfyUI-node/* ComfyUI/custom_nodes/
```

**Configuration**:
```yaml
anime4k:
  quality_level: 2  # 0-3
  processing_gpu: true
  parameters:
    denoise_level: 0.5
    edge_enhancement: 0.3
    color_enhancement: 0.2
```

### 1.7 CivitAI (Model Management)
**Purpose**: Download anime models locally

**Installation**:
```bash
pip install civitai-downloader
```

**Setup Script**:
```bash
#!/bin/bash
# Download essential models

# Checkpoints
civitai download \
  --model-id "anything-v4.5" \
  --type checkpoint \
  --output ComfyUI/models/checkpoints/

# LoRAs
civitai download \
  --model-id "anime-style-lora" \
  --type lora \
  --output ComfyUI/models/loras/

# VAEs
civitai download \
  --model-id "vae-anime" \
  --type vae \
  --output ComfyUI/models/vae/

# Embeddings
civitai download \
  --model-id "anime-embedding" \
  --type embedding \
  --output ComfyUI/models/embeddings/
```

## Phase 2: Vector & Graph Database Setup

### 2.1 ChromaDB (Vector Embeddings)
**Purpose**: Semantic search, embedding storage

**Installation**:
```bash
pip install chromadb
```

**Local Setup**:
```python
import chromadb
from chromadb.config import Settings

settings = Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db",
    anonymized_telemetry=False,
    allow_reset=True
)

client = chromadb.Client(settings)

# Create collections
assets_collection = client.get_or_create_collection(
    name="generated_assets",
    metadata={"hnsw:space": "cosine"}
)

trends_collection = client.get_or_create_collection(
    name="market_trends",
    metadata={"hnsw:space": "cosine"}
)
```

**Data Structure**:
```yaml
Asset Document:
  id: "asset-001"
  title: "Anime NFT #001"
  description: "High-quality anime character"
  embedding: [vector...]  # 768-dim from all-MiniLM-L6
  metadata:
    style: "anime"
    model_used: "anything-v4.5"
    loras: ["anime-style", "detailed"]
    upscaler: "Anime4K-v3.1"
    quality_score: 8.5
    generated_at: "2025-12-05T10:30:00Z"
```

### 2.2 Neo4j (Knowledge Graph)
**Purpose**: Relationship mapping, dependency tracking

**Installation**:
```bash
# Download Neo4j Desktop or Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Python driver
pip install neo4j
```

**Graph Schema**:
```cypher
# Nodes
CREATE (asset:Asset {id, title, model_used, style})
CREATE (trend:Trend {keyword, sentiment, volume})
CREATE (model:Model {name, type, source, version})
CREATE (lora:LoRA {name, style, checkpoint})
CREATE (user:User {address, preferences, history})

# Relationships
asset-[:GENERATED_FROM]-model
asset-[:USES_LORA]-lora
asset-[:BASED_ON]-trend
trend-[:TRENDS_IN]-platform
model-[:TRAINED_ON]-dataset
user-[:OWNS]-asset
user-[:INTERESTED_IN]-trend
```

**Python Implementation**:
```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", 
                           auth=("neo4j", "password"))

def create_asset_node(session, asset_data):
    session.run("""
        CREATE (a:Asset {
            id: $id,
            title: $title,
            model: $model,
            style: $style,
            created_at: datetime()
        })
    """, **asset_data)

def create_relationships(session, asset_id, model_id, lora_ids):
    session.run("""
        MATCH (a:Asset {id: $asset_id}), 
              (m:Model {id: $model_id})
        CREATE (a)-[:GENERATED_FROM]->(m)
    """, asset_id=asset_id, model_id=model_id)
```

### 2.3 Memory Storage (Persistent)
**Purpose**: Context retention, state management

**Installation**:
```bash
pip install faiss-cpu redis  # or sqlalchemy
```

**Implementation**:
```python
import json
from pathlib import Path

class PersistentMemory:
    def __init__(self, storage_dir="./memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def save_context(self, key, context):
        """Save execution context"""
        file_path = self.storage_dir / f"{key}.json"
        with open(file_path, 'w') as f:
            json.dump(context, f, indent=2)
    
    def load_context(self, key):
        """Load execution context"""
        file_path = self.storage_dir / f"{key}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    
    def memory_bank(self):
        """Get all memory contexts"""
        contexts = {}
        for file_path in self.storage_dir.glob("*.json"):
            with open(file_path, 'r') as f:
                contexts[file_path.stem] = json.load(f)
        return contexts
```

## Phase 3: Integration Layer

### 3.1 Unified API Interface
**File**: `packages/core/src/codeops/integrations/pipeline.py`

```python
from typing import Dict, List
from langgraph.graph import StateGraph
from chromadb import Client as ChromaClient
from neo4j import GraphDatabase
import asyncio

class EspalhaIntegrationPipeline:
    """Complete integration of all tools"""
    
    def __init__(self):
        self.firecrawl = FireCrawlClient()
        self.comfyui = ComfyUIClient()
        self.chromadb = ChromaClient()
        self.neo4j = GraphDatabase.driver("bolt://localhost:7687")
        self.memory = PersistentMemory()
        self.langgraph = self._setup_workflow()
    
    def _setup_workflow(self):
        """Setup LangGraph workflow"""
        workflow = StateGraph(PipelineState)
        workflow.add_node("fetch", self.fetch_trends)
        workflow.add_node("generate", self.generate_assets)
        workflow.add_node("vector_index", self.index_chromadb)
        workflow.add_node("graph_update", self.update_neo4j)
        workflow.add_node("memory_save", self.save_memory)
        
        workflow.add_edge("fetch", "generate")
        workflow.add_edge("generate", "vector_index")
        workflow.add_edge("vector_index", "graph_update")
        workflow.add_edge("graph_update", "memory_save")
        
        return workflow.compile()
    
    async def fetch_trends(self, state):
        """FireCrawl: Fetch market trends"""
        trends = await self.firecrawl.crawl_multiple([
            "https://twitter.com/search?q=nft+anime",
            "https://reddit.com/r/NFT"
        ])
        state["market_trends"] = trends
        return state
    
    async def generate_assets(self, state):
        """ComfyUI: Generate assets"""
        assets = []
        for trend in state["market_trends"]:
            # Use LangGraph to decide workflow
            workflow_config = self.langgraph.invoke({
                "trend": trend,
                "models": self.memory.load_context("available_models")
            })
            
            # Execute ComfyUI workflow
            generated = self.comfyui.execute_workflow(
                workflow_config,
                input_params={"prompt": trend["keyword"]}
            )
            assets.extend(generated)
        
        state["generated_assets"] = assets
        return state
    
    async def index_chromadb(self, state):
        """ChromaDB: Index embeddings"""
        collection = self.chromadb.get_or_create_collection(
            "generated_assets"
        )
        
        for asset in state["generated_assets"]:
            collection.add(
                ids=[asset["id"]],
                embeddings=[asset["embedding"]],
                metadatas=[{
                    "model": asset["model"],
                    "loras": asset["loras"],
                    "quality": asset["quality_score"]
                }],
                documents=[asset["description"]]
            )
        
        return state
    
    async def update_neo4j(self, state):
        """Neo4j: Update knowledge graph"""
        with self.neo4j.session() as session:
            for asset in state["generated_assets"]:
                session.run("""
                    CREATE (a:Asset {
                        id: $id,
                        title: $title,
                        model: $model,
                        created_at: datetime()
                    })
                    WITH a
                    MATCH (m:Model {id: $model_id})
                    CREATE (a)-[:GENERATED_FROM]->(m)
                """, 
                id=asset["id"],
                title=asset["title"],
                model=asset["model"],
                model_id=asset["model_id"]
                )
        
        return state
    
    async def save_memory(self, state):
        """Save execution context"""
        self.memory.save_context("last_execution", {
            "trends_processed": len(state["market_trends"]),
            "assets_generated": len(state["generated_assets"]),
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    async def run_full_pipeline(self):
        """Execute complete pipeline"""
        return await self.langgraph.ainvoke({
            "market_trends": [],
            "generated_assets": [],
            "embeddings": [],
            "graph_relationships": {},
            "memory_context": ""
        })
```

## Phase 4: Installation Scripts

### 4.1 Complete Setup Script
**File**: `scripts/install_espalha.sh`

```bash
#!/bin/bash
set -e

echo "🚀 Starting Espalha Integration Setup..."

# Create directories
mkdir -p ComfyUI/{models,custom_nodes,input,output}
mkdir -p databases/{chromadb,neo4j}
mkdir -p memory

# 1. FireCrawl
echo "📡 Installing FireCrawl..."
git clone https://github.com/mendableai/firecrawl.git || true
cd firecrawl
pip install -e .
cd ..

# 2. LangGraph
echo "🌳 Installing LangGraph..."
pip install langgraph langchain langchain-community

# 3. ComfyUI
echo "🎨 Installing ComfyUI..."
git clone https://github.com/comfyanonymous/ComfyUI.git || true
cd ComfyUI
pip install -r requirements.txt
cd ..

# 4. ComfyUI Extensions
echo "🔧 Installing ComfyUI Extensions..."
cd ComfyUI/custom_nodes
git clone https://github.com/comfyanonymous/ComfyUI-Manager.git || true
git clone https://github.com/ArtVentureX/ArtVenture-Nodes.git || true
cd ../..

# 5. Anime4K
echo "🎬 Installing Anime4K..."
git clone https://github.com/bloc97/Anime4KCPP.git || true
cd Anime4KCPP
mkdir -p build
cd build
cmake ..
make
cd ../..
pip install anime4kcpp

# 6. CivitAI
echo "🤖 Installing CivitAI Downloader..."
pip install civitai-downloader

# 7. Databases
echo "📊 Installing Databases..."
pip install chromadb neo4j

# 8. Download Models
echo "📥 Downloading Models..."
mkdir -p ComfyUI/models/{checkpoints,loras,vae,embeddings}

echo "✅ Espalha Integration Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/download_models.sh"
echo "2. Start Neo4j: docker run -d -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest"
echo "3. Start ComfyUI: cd ComfyUI && python main.py"
echo "4. Run pipeline: python -m codeops.integrations.pipeline"
```

### 4.2 Model Download Script
**File**: `scripts/download_models.sh`

```bash
#!/bin/bash

echo "📥 Downloading anime models..."

# Checkpoints
civitai download \
  --model "Anything v4.5 Pruned" \
  --output ComfyUI/models/checkpoints/

civitai download \
  --model "Chilled Remix" \
  --output ComfyUI/models/checkpoints/

# LoRAs
civitai download \
  --model "Anime Style LoRA" \
  --output ComfyUI/models/loras/

civitai download \
  --model "Detailed Hands" \
  --output ComfyUI/models/loras/

# VAEs
civitai download \
  --model "Anime VAE" \
  --output ComfyUI/models/vae/

echo "✅ Models downloaded!"
```

## Phase 5: Configuration Files

### 5.1 Main Configuration
**File**: `config/espalha.yaml`

```yaml
espalha_pipeline:
  version: "1.0.0"
  
  firecrawl:
    enabled: true
    api_endpoint: "http://localhost:3000"
    max_depth: 3
    timeout: 30000
  
  langgraph:
    enabled: true
    workflow_file: "workflows/pipeline.yaml"
  
  comfyui:
    enabled: true
    api_endpoint: "http://localhost:8188"
    web_endpoint: "http://localhost:8188/api"
    mcp_enabled: true
    mcp_port: 5000
  
  comfyui_cli:
    enabled: true
    batch_size: 4
    gpu_device: 0
  
  anime4k:
    enabled: true
    quality_level: 2
    gpu_acceleration: true
  
  civitai:
    enabled: true
    auto_download: true
    update_interval: 7  # days
  
  chromadb:
    enabled: true
    persist_directory: "./chroma_db"
    collections:
      - name: "generated_assets"
        space: "cosine"
      - name: "market_trends"
        space: "cosine"
  
  neo4j:
    enabled: true
    uri: "bolt://localhost:7687"
    auth: ["neo4j", "password"]
  
  memory:
    enabled: true
    storage_dir: "./memory"
    auto_backup: true
    backup_interval: 3600  # seconds
```

## Phase 6: Execution Flow

### 6.1 Complete Pipeline Execution

```
START
  ↓
1. FireCrawl: Scrape trends
  ├─ Twitter (anime NFT)
  ├─ Reddit (NFT community)
  └─ YouTube (trends)
  ↓
2. LangGraph: Analyze & decide
  ├─ Trend analysis
  ├─ Sentiment analysis
  └─ Strategy generation
  ↓
3. ComfyUI: Generate assets
  ├─ Download models (CivitAI)
  ├─ Execute workflow
  └─ Generate images
  ↓
4. Anime4K: Upscale
  ├─ Denoise
  ├─ Enhance edges
  └─ Color enhancement
  ↓
5. ChromaDB: Index
  ├─ Generate embeddings
  ├─ Store vectors
  └─ Enable search
  ↓
6. Neo4j: Graph update
  ├─ Create nodes
  ├─ Add relationships
  └─ Update knowledge graph
  ↓
7. Memory: Save context
  ├─ Save execution log
  ├─ Cache metadata
  └─ Backup state
  ↓
END (Assets ready for publishing)
```

## Implementation Checklist

### Installation
- [ ] FireCrawl installed & configured
- [ ] LangGraph installed
- [ ] ComfyUI installed with models
- [ ] ComfyUIMCP configured
- [ ] ComfyUICLI working
- [ ] Anime4K installed
- [ ] CivitAI models downloaded
- [ ] ChromaDB running
- [ ] Neo4j running
- [ ] Memory storage setup

### Integration
- [ ] API interfaces created
- [ ] LangGraph workflow defined
- [ ] FireCrawl nodes ready
- [ ] ComfyUI API endpoints connected
- [ ] Anime4K pipeline integrated
- [ ] ChromaDB collections created
- [ ] Neo4j schema deployed
- [ ] Memory persistence working

### Testing
- [ ] Individual tool tests pass
- [ ] Integration tests pass
- [ ] Full pipeline test successful
- [ ] Database queries working
- [ ] Memory retrieval working
- [ ] Workflow automation verified

### Documentation
- [ ] Setup instructions
- [ ] API documentation
- [ ] Configuration guide
- [ ] Troubleshooting guide
- [ ] Performance optimization tips

## Performance Targets

| Component | Metric | Target |
|-----------|--------|--------|
| FireCrawl | Pages/min | 10+ |
| ComfyUI | Images/hour | 50+ |
| Anime4K | Upscale speed | 2s per 512x512 |
| ChromaDB | Query latency | <100ms |
| Neo4j | Node creation | <50ms |
| Memory | Save latency | <10ms |

## Next Steps

1. ✅ Create installation scripts
2. ✅ Download and configure each tool
3. ✅ Setup databases locally
4. ✅ Create integration layer
5. ✅ Test individual components
6. ✅ Test full pipeline
7. ✅ Deploy to production
8. ✅ Monitor and optimize
