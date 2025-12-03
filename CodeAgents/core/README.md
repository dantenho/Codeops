# 🧠 RAG & METRICS ARCHITECTURE

## 📚 Vector Database (ChromaDB)
The system uses **ChromaDB** as the primary vector store for code retrieval.

### Configuration
- **Persistence:** `./chroma_db`
- **Collection:** `codebase`
- **Embedding Model:** `all-MiniLM-L6-v2` (Sentence Transformers)
- **Hardware Acceleration:** Automatically detects CUDA (GPU) availability.

### Usage
```python
from CodeAgents.core.rag import rag_engine

# Add documents
rag_engine.add_documents(
    documents=["def hello(): print('world')"],
    metadatas=[{"source": "main.py"}],
    ids=["doc1"]
)

# Search
results = rag_engine.search("print function")
```

## 📊 Metrics System
The metrics engine aggregates JSON telemetry logs from `CodeAgents/`.

### Key Metrics
- **Success Rate:** Percentage of successful operations.
- **Error Severity:** Breakdown of errors by severity (LOW to CRITICAL).
- **Performance:** Average operation duration.

### Usage
```python
from CodeAgents.core.metrics import metrics_engine

# Get report for last 7 days
report = metrics_engine.generate_report(days=7)
print(report)
```

## 📡 Telemetry System
Standardized logging ensures all agent actions are traceable.

### Usage
```python
from CodeAgents.core.telemetry import telemetry, OperationLog

telemetry.log_operation(OperationLog(
    agent="GrokIA",
    operation="CREATE",
    target={"file": "test.py"},
    status="SUCCESS"
))
```
