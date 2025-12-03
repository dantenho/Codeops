# Database Strategy and Configuration

## Overview

EudoraX Prototype uses a **multi-database strategy** to optimize for different data types and access patterns. The primary database is **ChromaDB** for vector embeddings, with optional support for relational, graph, and document databases.

## Database Architecture

### Primary: ChromaDB (Vector Database)

**Use Case**: Embeddings for images, text, code, and agent learning

**Why ChromaDB?**

- ✅ Optimized for similarity search
- ✅ Simple Python API
- ✅ Local-first with persistence
- ✅ No external server required
- ✅ Perfect for ML embeddings

**Location**: `CodeAgents/Training/chroma_db/`

**Collections**:

- `images`: Image CLIP embeddings and metadata
- `agent_knowledge`: Agent learning data and experiences
- `conversations`: Chat history embeddings
- `code_snippets`: Code embeddings for semantic search

---

## ChromaDB Setup

### Installation

ChromaDB is included in `tools/Pylorix/requirements.txt`:

```bash
pip install chromadb==0.5.18
```

### Basic Configuration

```python
import chromadb
from chromadb.config import Settings

# Persistent storage (recommended)
client = chromadb.PersistentClient(
    path="./CodeAgents/Training/chroma_db"
)

# Create or get collection
collection = client.get_or_create_collection(
    name="images",
    metadata={"description": "Image embeddings from Pylorix"}
)
```

### Environment Variables

Add to your `.env` file:

```env
# ChromaDB Configuration
CHROMA_DB_PATH=./CodeAgents/Training/chroma_db
CHROMA_DEFAULT_COLLECTION=images
```

### Data Operations

#### Adding Embeddings

```python
# Add image with CLIP embedding
collection.add(
    embeddings=[[0.1, 0.2, ..., 0.5]],  # 512-dim CLIP vector
    documents=["A cyberpunk city at night with neon lights"],
    metadatas=[{
        "source": "pylorix",
        "model": "FLUX.2-dev",
        "timestamp": "2025-12-03T05:13:37Z",
        "dimensions": "1024x1024"
    }],
    ids=["img_001"]
)
```

#### Querying by Similarity

```python
# Search similar images
results = collection.query(
    query_embeddings=[[0.1, 0.2, ..., 0.5]],  # Query vector
    n_results=10,
    where={"source": "pylorix"}  # Optional filter
)

# Results include:
# - ids: List of matched IDs
# - distances: Similarity scores
# - documents: Original text
# - metadatas: Associated metadata
```

#### Updating Metadata

```python
collection.update(
    ids=["img_001"],
    metadatas=[{"quality_score": 95, "upscaled": True}]
)
```

#### Deleting Entries

```python
collection.delete(ids=["img_001"])
```

---

## Alternative Databases

The `tools/Pylorix` Database Testing feature benchmarks 5 different databases. Use the Gradio UI to test and compare:

### 1. Supabase (Cloud Relational + Storage)

**Use Case**: Full-stack applications with auth, storage, and real-time features

**Pros**:

- ✅ Managed PostgreSQL in the cloud
- ✅ Built-in authentication
- ✅ Real-time subscriptions
- ✅ File storage included
- ✅ Generous free tier

**Cons**:

- ❌ Requires internet connection
- ❌ Not optimized for vectors (without pgvector extension)

**Setup**:

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Get URL and anon key from Settings > API

**Configuration**:

```env
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

**Python Example**:

```python
from supabase import create_client

supabase = create_client(supabase_url, supabase_key)

# Insert data
data = supabase.table("images").insert({
    "description": "Cyberpunk city",
    "model": "FLUX.2-dev",
    "created_at": "2025-12-03T05:13:37Z"
}).execute()

# Query
results = supabase.table("images").select("*").eq("model", "FLUX.2-dev").execute()
```

**Schema Example**:

```sql
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description TEXT,
    model VARCHAR(50),
    file_path TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_images_model ON images(model);
```

---

### 2. PostgreSQL (Local Relational)

**Use Case**: Relational data, complex queries, ACID transactions

**Pros**:

- ✅ Mature and reliable
- ✅ Advanced SQL features
- ✅ pgvector extension for embeddings
- ✅ Local control

**Cons**:

- ❌ Requires separate server
- ❌ More complex setup

**Setup**:

1. Install PostgreSQL:

```bash
# Windows (with Chocolatey)
choco install postgresql

# Ubuntu
sudo apt install postgresql

# macOS (with Homebrew)
brew install postgresql
```

2. Start service:

```bash
# Windows
net start postgresql

# Unix/macOS
brew services start postgresql
```

3. Create database:

```bash
createdb eudorax_prototype
```

**Configuration**:

```env
# .env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eudorax_prototype
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

**Python Example**:

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="eudorax_prototype",
    user="postgres",
    password="password"
)

cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS images (
        id SERIAL PRIMARY KEY,
        description TEXT,
        model VARCHAR(50),
        created_at TIMESTAMP DEFAULT NOW()
    )
""")

# Insert
cursor.execute("""
    INSERT INTO images (description, model)
    VALUES (%s, %s)
""", ("Cyberpunk city", "FLUX.2-dev"))

conn.commit()
```

**pgvector Extension** (for embeddings):

```sql
-- Install extension
CREATE EXTENSION vector;

-- Add vector column
ALTER TABLE images ADD COLUMN embedding vector(512);

-- Search by similarity
SELECT * FROM images
ORDER BY embedding <-> '[0.1, 0.2, ..., 0.5]'
LIMIT 10;
```

---

### 3. Neo4j (Graph Database)

**Use Case**: Relationship mapping, model lineage, agent collaboration graphs

**Pros**:

- ✅ Native graph storage
- ✅ Cypher query language
- ✅ Visual graph exploration
- ✅ Great for relationships

**Cons**:

- ❌ Requires separate server
- ❌ Different query paradigm

**Setup**:

1. Install Neo4j Desktop: [neo4j.com/download](https://neo4j.com/download/)
2. Create new database
3. Set password

**Configuration**:

```env
# .env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

**Python Example**:

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

def create_model(tx, name, version):
    tx.run("""
        CREATE (m:Model {name: $name, version: $version})
    """, name=name, version=version)

with driver.session() as session:
    session.execute_write(create_model, "FLUX.2-dev", "1.0")
```

**Use Case Example** (Model Lineage):

```cypher
// Create model lineage
CREATE (base:Model {name: "Stable Diffusion 1.5"})
CREATE (lora:LoRA {name: "Anime Style"})
CREATE (output:Image {prompt: "Anime girl"})

CREATE (base)-[:TRAINED_WITH]->(lora)
CREATE (lora)-[:GENERATED]->(output)

// Query: Find all images from a specific LoRA
MATCH (l:LoRA {name: "Anime Style"})-[:GENERATED]->(i:Image)
RETURN i
```

---

### 4. MongoDB (Document Database)

**Use Case**: Flexible schemas, JSON-like documents

**Pros**:

- ✅ Flexible schema
- ✅ JSON-native
- ✅ Good for evolving data models
- ✅ Horizontal scaling

**Cons**:

- ❌ No ACID transactions (limited)
- ❌ Not optimized for vectors

**Setup**:

1. Install MongoDB: [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
2. Start service

**Configuration**:

```env
# .env
MONGO_CONNECTION_STRING=mongodb://localhost:27017/
MONGO_DATABASE=eudorax_prototype
```

**Python Example**:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["eudorax_prototype"]
collection = db["images"]

# Insert
collection.insert_one({
    "description": "Cyberpunk city",
    "model": "FLUX.2-dev",
    "metadata": {
        "width": 1024,
        "height": 1024,
        "steps": 30
    },
    "created_at": "2025-12-03T05:13:37Z"
})

# Query
results = collection.find({"model": "FLUX.2-dev"})
```

---

## Database Testing Tool

Pylorix includes a comprehensive database testing feature to benchmark and compare different databases.

### Access the Tool

1. Launch Pylorix:

```bash
cd tools/Pylorix
python app.py
```

2. Navigate to **"🔬 Database Testing"** tab

3. Configure databases in the **"⚙️ Configure Databases"** tab

4. Click **"🚀 Test All Enabled Databases"**

### Scoring System

Each database is graded on:

- **Connection Time** (20 points)
- **Write Performance** (25 points)
- **Read Performance** (25 points)
- **Query Performance** (20 points)
- **Reliability** (10 points)

**Grades**:

- **A+** (90-100): Excellent, recommended
- **A** (80-89): Very good
- **B** (70-79): Good
- **C** (60-69): Acceptable
- **D** (50-59): Poor
- **F** (<50): Not recommended

### Typical Results

| Database | Score | Grade | Best For |
|----------|-------|-------|----------|
| ChromaDB | 95 | A+ | Vector embeddings |
| Supabase | 85 | A | Cloud applications |
| PostgreSQL | 82 | A | Relational data |
| MongoDB | 78 | B | Flexible schemas |
| Neo4j | 75 | B | Graph relationships |

---

## Migration Guides

### ChromaDB → PostgreSQL (with pgvector)

```python
import chromadb
import psycopg2

# Source: ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("images")

# Destination: PostgreSQL
conn = psycopg2.connect(...)
cursor = conn.cursor()

# Get all data from ChromaDB
results = collection.get(include=["embeddings", "documents", "metadatas"])

# Insert into PostgreSQL
for i, embedding in enumerate(results["embeddings"]):
    cursor.execute("""
        INSERT INTO images (description, embedding, metadata)
        VALUES (%s, %s, %s)
    """, (
        results["documents"][i],
        embedding,
        results["metadatas"][i]
    ))

conn.commit()
```

### File System → ChromaDB

```python
import json
from pathlib import Path
import chromadb

# Load JSON logs
logs_dir = Path("CodeAgents/AgentName/logs")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("agent_operations")

for log_file in logs_dir.glob("*.json"):
    with open(log_file) as f:
        data = json.load(f)

    # Add to ChromaDB (requires embedding - use text for basic storage)
    collection.add(
        documents=[json.dumps(data)],
        metadatas=[{"agent": data["agent"], "timestamp": data["timestamp"]}],
        ids=[log_file.stem]
    )
```

---

## Best Practices

### 1. Choose the Right Database

| Data Type | Recommended Database |
|-----------|---------------------|
| ML Embeddings | ChromaDB |
| User accounts, structured data | PostgreSQL / Supabase |
| Flexible JSON documents | MongoDB |
| Relationships, lineage | Neo4j |
| Files (images, models) | File System + Supabase Storage |

### 2. Connection Pooling

```python
# Don't create new connection per request
# BAD:
def query():
    client = chromadb.PersistentClient(...)  # New each time
    return client.get_collection(...)

# GOOD:
client = chromadb.PersistentClient(...)  # Once at startup
def query():
    return client.get_collection(...)
```

### 3. Batch Operations

```python
# Add multiple items at once
collection.add(
    embeddings=[emb1, emb2, emb3],  # Batch
    documents=[doc1, doc2, doc3],
    ids=["1", "2", "3"]
)
```

### 4. Regular Backups

```bash
# ChromaDB backup (copy directory)
cp -r CodeAgents/Training/chroma_db backups/chroma_$(date +%Y%m%d)

# PostgreSQL backup
pg_dump eudorax_prototype > backup_$(date +%Y%m%d).sql
```

### 5. Monitoring

```python
# Get collection stats
collection_stats = collection.count()
print(f"Total vectors: {collection_stats}")

# Check disk usage
import os
db_path = "CodeAgents/Training/chroma_db"
size_mb = sum(f.stat().st_size for f in Path(db_path).rglob('*')) / 1024 / 1024
print(f"Database size: {size_mb:.2f} MB")
```

---

## Troubleshooting

### ChromaDB: "Collection not found"

```python
# Create collection if it doesn't exist
collection = client.get_or_create_collection("images")
```

### Supabase: "API key invalid"

Check your `.env`:

```bash
# Ensure anon key, not service_role key
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### PostgreSQL: "Connection refused"

```bash
# Check if server is running
# Windows
services.msc  # Look for postgresql

# Unix/macOS
pg_isready
```

### Neo4j: "Authentication failed"

Reset password in Neo4j Desktop or:

```bash
neo4j-admin set-initial-password new_password
```

---

## Performance Tuning

### ChromaDB

```python
# Use batch queries
results = collection.query(
    query_embeddings=[vec1, vec2, vec3],  # Multiple at once
    n_results=10
)

# Limit returned fields
results = collection.get(
    ids=["1", "2"],
    include=["metadatas"]  # Don't fetch embeddings if not needed
)
```

### PostgreSQL

```sql
-- Add indexes
CREATE INDEX idx_images_created_at ON images(created_at);
CREATE INDEX idx_images_model ON images(model);

-- Use EXPLAIN to analyze queries
EXPLAIN ANALYZE SELECT * FROM images WHERE model = 'FLUX.2-dev';
```

---

**Last Updated**: 2025-12-03
**For Questions**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
