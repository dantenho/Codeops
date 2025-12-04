# EudoraX Development Plan & Roadmap

## 1. Project Overview
Restructuring the EudoraX Prototype to leverage SOTA technologies for RAG and Multi-Agent systems.

## 2. Instruction Evaluation
- **Current State**: Project contains scattered scripts and needs consolidation.
- **Goal**: Create a unified, modular architecture.

## 3. SOTA Technology Stack Recommendations
### Core Frameworks
- **Orchestration**: LangChain or LangGraph (for complex agent flows).
- **RAG**: LlamaIndex (specialized for data ingestion/retrieval).
- **Vector Database**: ChromaDB (Local/Server, highly compatible).

### Advanced Capabilities
- **Optimization**: DSPy (for prompt optimization).
- **Serving**: vLLM (for high-performance local inference if using CUDA).

## 4. Roadmap
1.  **Cleanup**: Remove temporary files and deprecated scripts.
2.  **Structure**:
    - /src: Main source code.
    - /tests: Pytest suite.
    - /docs: Documentation.
3.  **Implementation**:
    - Initialize ChromaDB with persistent storage.
    - Implement RAG pipeline using LlamaIndex/LangChain.
    - Create Agentic workflow for task automation.
4.  **Testing**:
    - Simulate tests across different git branches.
