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
from eudorax.core.telemetry import TelemetryManager
from eudorax.core.rag import RAGEngine

# Initialize telemetry
telemetry = TelemetryManager(agent_name="MyAgent")

# Log an operation
telemetry.log_operation(
    operation="CREATE",
    target={"file": "example.py"},
    status="SUCCESS"
)

# Initialize RAG engine
rag = RAGEngine(collection_name="codebase_knowledge")
rag.index_document("example.py", content="...")
results = rag.search("function definition", top_k=5)
```

## Architecture

### Core Modules

- **`core/`** - Core system modules
  - `telemetry.py` - Structured logging system
  - `rag.py` - RAG engine with ChromaDB
  - `skeleton_generator.py` - Agent structure generator
  - `access_control.py` - Access control system
  - `metrics.py` - Performance metrics
  - `cli.py` - Command-line interface

### Agents

- **`agents/composer/`** - Composer agent with analysis tools
- **`agents/deepseek-r1/`** - DeepSeekR1 telemetry and analysis
- **`agents/gpt-5-codex/`** - GPT-5.1-Codex implementation
- **`agents/claude-code/`** - Claude Code agent

### Training System

- **`training/`** - Structured learning paths
  - Progressive training levels (01-05)
  - Assessment and progress tracking
  - Knowledge extraction and memory persistence

### Evaluation

- **`evaluation/`** - Quality gates and metrics
  - Code quality validation
  - Performance benchmarking
  - Compliance checking

### GitHub Integration

- **`github/`** - GitHub optimization detection
  - Comment processing
  - Optimization pattern detection
  - Code improvement suggestions

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
├── packages/                    # Modern workspace packages
│   ├── core/                   # Core system modules (telemetry, RAG, metrics)
│   ├── training/               # Training system with token tracking
│   ├── evaluation/             # Quality gates and code evaluation
│   ├── github-integration/     # GitHub PR optimization
│   ├── error-intelligence/     # Error diagnosis and self-healing
│   ├── vibecode/               # Natural language code generation
│   ├── backend-api/            # FastAPI backend
│   ├── memory/                 # Memory management
│   └── skeleton-generator/     # Agent skeleton generation
├── CodeAgents/                 # Agent runtime data (logs, analysis)
├── config/                     # Configuration files
├── docs/                       # Documentation
├── tests/                      # Test suite
├── structures/                 # Agent skeleton templates
└── scripts/                    # Utility scripts
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
python packages/skeleton-generator/scripts/complete_skeleton_generator.py --agent-id MyAgent
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
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md) - Current project status and roadmap

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- Built following the Agents.MD protocol
- Uses ChromaDB for vector storage
- Integrates with GitHub for code review optimization
