# Multi-Agent Coding System

A sophisticated multi-agent framework for collaborative AI-powered software development, featuring telemetry logging, RAG (Retrieval-Augmented Generation), structured training systems, and comprehensive quality gates.

## Overview

This system enables multiple AI agents to work collaboratively on codebases while maintaining:
- **Structured telemetry** for operation tracking
- **RAG-powered knowledge retrieval** using ChromaDB
- **Agent skeleton generation** for consistent structure
- **Training systems** for skill reinforcement
- **Quality gates** for code validation
- **GitHub integration** for optimization detection

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for NVM)
- UV package manager (for Python)
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd urb

# Create virtual environment using UV
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

### Basic Usage

```python
from CodeAgents.core.telemetry import TelemetryManager, OperationLog
from CodeAgents.core.rag import RAGEngine, get_rag_engine

# Initialize telemetry
telemetry = TelemetryManager()

# Log an operation
log = OperationLog(
    agent="MyAgent",
    operation="CREATE",
    target={"file": "example.py"},
    status="SUCCESS"
)
telemetry.log_operation(log)

# Initialize RAG engine
rag = get_rag_engine(collection_name="codebase_knowledge")
rag.index_document("example.py", content="...")
results = rag.search("function definition", top_k=5)
```

## Architecture

### Core Modules

- **`CodeAgents/core/`** - Core system modules
  - `telemetry.py` - Structured logging system
  - `rag.py` - RAG engine with ChromaDB
  - `skeleton_generator.py` - Agent structure generator
  - `access_control.py` - Access control system
  - `metrics.py` - Performance metrics
  - `cli.py` - Command-line interface

### Agents

- **`CodeAgents/{AgentName}/`** - Per-agent directories
  - `logs/` - Operation telemetry
  - `errors/` - Error logs
  - `analysis/` - Analysis reports

### Training System

- **`CodeAgents/Training/`** - Structured learning paths
  - Progressive training levels (01-05)
  - Assessment and progress tracking
  - Knowledge extraction and memory persistence

### Evaluation

- **`CodeAgents/Evaluation/`** - Quality gates and metrics
  - Code quality validation
  - Performance benchmarking
  - Compliance checking

### GitHub Integration

- **`CodeAgents/GitHub/`** - GitHub optimization detection
  - Comment processing
  - Optimization pattern detection
  - Code improvement suggestions

### Backend API

- **`CodeAgents/backend/`** - FastAPI backend server
  - Evaluation endpoints
  - Telemetry endpoints
  - Health checks

## Agent Protocol

All agents must follow the **Agents.MD** protocol, which defines:

- **Memory & Context Protocol** - Agent-specific memory files
- **Environment Requirements** - NVM/UV usage, package management
- **Terminal Execution Protocol** - Safe auto-run guidelines
- **Telemetry System** - Structured logging with JSON schemas
- **Code Structure** - Python code templates and documentation standards
- **GitHub Integration** - Branch naming, PR workflows

See [`Agents.MD`](Agents.MD) for complete protocol documentation.

## Project Structure

```
CodeAgents/
├── core/                # Core system modules
├── Training/            # Training system
├── Evaluation/         # Quality gates and metrics
├── GitHub/              # GitHub integration
├── Errors/              # Error intelligence
├── VibeCode/            # Vibe coding engine
├── backend/             # Backend API
├── Memory/              # Agent memory files
├── schemas/             # JSON schemas
└── {AgentName}/         # Per-agent directories

config/                  # Configuration files
docs/                    # Documentation
tests/                   # Test files
scripts/                  # Utility scripts
Structures/              # Agent templates
```

## Development

### Code Quality

The project uses:
- **Ruff** - Fast Python linter
- **Black** - Code formatter
- **MyPy** - Type checking
- **Pydocstyle** - Docstring validation

Run quality checks:
```bash
ruff check .
black --check .
mypy .
```

### Telemetry

All agents must log operations using the telemetry system:

```python
from core.telemetry import TelemetryManager

telemetry = TelemetryManager(agent_name="AgentName")
telemetry.log_operation(
    operation="CREATE",
    target={"file": "path/to/file.py"},
    status="SUCCESS",
    duration_ms=150
)
```

### Creating a New Agent

1. Generate skeleton structure:
```bash
python skeleton-generator/scripts/complete_skeleton_generator.py --agent-id MyAgent
```

2. Create memory file at `CodeAgents/Memory/MyAgent.md`

3. Implement agent following Agents.MD protocol

4. Add telemetry logging for all operations

## Documentation

- [`Agents.MD`](Agents.MD) - Complete agent protocol
- [`docs/SKELETON_STRUCTURE.md`](docs/SKELETON_STRUCTURE.md) - Skeleton structure guide
- [`docs/DATABASE.md`](docs/DATABASE.md) - Database schemas
- [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) - Workflow documentation
- [`CONTRIBUTING.md`](CONTRIBUTING.md) - Contribution guidelines

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- Built following the Agents.MD protocol
- Uses ChromaDB for vector storage
- Integrates with GitHub for code review optimization
