# EudoraX Prototype

**Multi-Agent AI Development Workspace**

EudoraX Prototype is an advanced development environment designed for collaborative AI agent workflows, featuring specialized tools for image processing, model management, and multi-agent coordination.

## 🌟 Features

### 🤖 Multi-Agent Framework (CodeAgents)
- **Collaborative AI System**: Multiple specialized AI agents (Claude, Gemini, GPT, Grok) working together
- **Telemetry & Logging**: Comprehensive agent activity tracking with JSON-formatted logs
- **Access Control**: Fine-grained permissions for agent operations
- **Training Database**: ChromaDB-powered vector storage for agent learning

### 🎨 Pylorix - Advanced Image Processing Suite
A comprehensive Gradio-based platform with 8 integrated features:

- **FLUX.2 Text-to-Image**: Generate high-quality images using Black Forest Labs' FLUX.2-dev model
- **Image Evaluation**: CLIP scores, ViT features, and quality metrics (PSNR, SSIM, LPIPS)
- **Upscaling**: Multiple algorithms (Real-ESRGAN, SwinIR, Bicubic, Lanczos)
- **Light Correction**: Automatic exposure correction and histogram optimization
- **Retinex Enhancement**: SSR, MSR, and MSRCR algorithms
- **3D LUTs**: Color grading with custom LUT files and presets
- **LoRA Training**: Fine-tune diffusion models with Low-Rank Adaptation
- **Vector & Mesh Database**: Local storage for embeddings and 3D assets
- **Database Testing**: Performance benchmarking for Supabase, PostgreSQL, ChromaDB, Neo4j, MongoDB

### 🎭 Civitai Integration
- **Model Discovery**: Search and browse Civitai's model repository
- **Download Manager**: Automated model version downloads
- **Civitai Link**: Real-time socket.io connection for model synchronization
- **API Client**: Full REST API integration

### 🛠️ Additional Tools
- **ComfyUI**: Node-based workflow for Stable Diffusion (submodule)
- **Playwright**: Browser automation for testing
- **Firecrawler**: Web scraping and data extraction

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.10+ (3.12 recommended)
- **Node.js**: 20+ (for frontend tools)
- **GPU**: NVIDIA GPU with 16GB+ VRAM (recommended for FLUX.2)
- **RAM**: 16GB+ system RAM

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Eudora-IA/Prototype.git
cd Prototype
```

2. **Set up Python environment with UV (recommended):**
```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix/MacOS:
source .venv/bin/activate

# Install dependencies
uv pip install -r tools/Pylorix/requirements.txt
uv pip install -r backend/requirements.txt
```

3. **Alternative: Use traditional pip:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r tools/Pylorix/requirements.txt
```

4. **Launch Pylorix:**
```bash
cd tools/Pylorix
python app.py
```
The Gradio interface will open at `http://localhost:7860`

5. **Run Backend API (optional):**
```bash
cd backend
python main.py
```

## 📁 Project Structure

```
EudoraX Prototype/
├── CodeAgents/              # Multi-agent collaboration framework
│   ├── Antigravity/         # Google Antigravity agent
│   ├── ClaudeCode/          # Anthropic Claude agent
│   ├── GeminiFlash25/       # Google Gemini Flash agent
│   ├── GeminiPro25/         # Google Gemini Pro agent
│   ├── Training/            # Agent training data & ChromaDB
│   ├── Memory/              # Shared agent memory
│   └── access_control.json  # Agent permissions
│
├── tools/                   # Specialized development tools
│   ├── Pylorix/            # Image processing & ML suite
│   ├── Civitai/            # Model management integration
│   ├── ComfyUI/            # Workflow-based generation
│   ├── Playwright/         # Browser automation
│   └── Firecrawler/        # Web scraping
│
├── backend/                 # FastAPI backend services
│   ├── main.py             # API server
│   ├── core/               # Core modules
│   └── requirements.txt    # Backend dependencies
│
├── libs/                    # Third-party libraries
│   ├── firecrawl/          # Web crawling library
│   ├── playwright/         # Browser automation lib
│   └── ComfyUI/            # Stable Diffusion library
│
├── .github/                 # GitHub workflows & templates
│   └── workflows/          # CI/CD automation
│
├── Agents.MD               # Multi-agent protocol specification
└── README.md               # This file
```

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture and design
- **[docs/DATABASE.md](docs/DATABASE.md)**: Database strategy and setup
- **[docs/WORKFLOWS.md](docs/WORKFLOWS.md)**: GitHub Actions workflows
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines
- **[Agents.MD](Agents.MD)**: Multi-agent protocol specification
- **[tools/Pylorix/README.md](tools/Pylorix/README.md)**: Pylorix documentation

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Civitai API (optional)
CIVITAI_API_KEY=your_api_key_here

# Database (optional - defaults to local ChromaDB)
CHROMA_DB_PATH=./CodeAgents/Training/chroma_db

# FLUX.2 Model (optional)
FLUX_MODEL_PATH=./models/flux-2-dev
```

### Database Setup
The project uses **ChromaDB** by default for vector embeddings. See [docs/DATABASE.md](docs/DATABASE.md) for:
- ChromaDB configuration
- Alternative databases (Supabase, PostgreSQL, Neo4j, MongoDB)
- Migration guides
- Performance benchmarking

## 🤝 Contributing

We follow a multi-agent development protocol. Please read:
1. **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines
2. **[Agents.MD](Agents.MD)**: Agent protocol requirements
3. **[docs/WORKFLOWS.md](docs/WORKFLOWS.md)**: GitHub Actions workflows

### Quick Contribution Checklist
- ✅ Follow Python code standards (Black, Ruff, isort)
- ✅ Add docstrings (Google style, 70%+ coverage)
- ✅ Include operation tags: `[CREATE]`, `[REFACTOR]`, `[DEBUG]`, `[MODIFY]`
- ✅ Add agent signature in comments
- ✅ Write commit messages in English
- ✅ Test changes locally before PR

## 🏗️ Development Workflow

### 1. Agent-Based Development
Each AI agent follows the protocol defined in `Agents.MD`:
- **Telemetry Logging**: All operations logged to `CodeAgents/{AgentName}/logs/`
- **Operation Tags**: Code changes tagged with operation type
- **Validation**: Automated GitHub Actions check compliance

### 2. GitHub Actions
Automated workflows validate:
- ✅ Docstring coverage (90% target)
- ✅ Code quality (Ruff, Black, MyPy)
- ✅ Agent compliance (operation tags, signatures)
- ✅ Telemetry schema validation

### 3. Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch
- `agent/{AgentName}/{feature}`: Feature branches

## 🧪 Testing

### Run Pylorix Tests
```bash
cd tools/Pylorix
pytest tests/
```

### Database Performance Testing
Use the built-in database testing tab in Pylorix to benchmark:
- Supabase
- PostgreSQL
- ChromaDB
- Neo4j
- MongoDB

## 📊 Key Technologies

- **Backend**: Python 3.12, FastAPI, Gradio
- **AI/ML**: FLUX.2, CLIP, ViT, Real-ESRGAN, SwinIR
- **Databases**: ChromaDB, Supabase, PostgreSQL, Neo4j, MongoDB
- **Tools**: UV package manager, Ruff, Black, MyPy
- **CI/CD**: GitHub Actions, CircleCI
- **APIs**: Civitai REST API, Socket.IO

## 🔗 Useful Links

- **[Civitai](https://civitai.com/)**: AI art model repository
- **[Black Forest Labs](https://blackforestlabs.ai/)**: FLUX.2 model creators
- **[ChromaDB](https://www.trychroma.com/)**: Vector database
- **[Gradio](https://gradio.app/)**: ML web interfaces

## 📜 License

MIT License - See [LICENSE](LICENSE) for details

## 🆘 Troubleshooting

### FLUX.2 Model Download Issues
- Ensure ~32GB free disk space
- Model auto-downloads on first use
- Manual download: Place in `tools/Pylorix/FLUX.2-dev/`

### ChromaDB Persistence
- Default path: `CodeAgents/Training/chroma_db`
- Configure via `CHROMA_DB_PATH` environment variable

### GPU Memory Issues
- Reduce batch size in LoRA training
- Use smaller FLUX.2 inference steps
- Close other GPU applications

### Import Errors
```bash
# Reinstall dependencies
uv pip install --force-reinstall -r tools/Pylorix/requirements.txt
```

## 🎯 Roadmap

- [ ] Complete Real-ESRGAN integration
- [ ] Implement SwinIR upscaling
- [ ] Finish LoRA training pipeline
- [ ] Add CLIP/ViT embeddings to vector DB
- [ ] Web UI for backend API
- [ ] Docker containerization
- [ ] Cloud deployment guides

## 👥 Contributors

This project is developed collaboratively by multiple AI agents:
- **Antigravity** (Google DeepMind)
- **Claude** (Anthropic)
- **Gemini** (Google)
- **GPT** (OpenAI)
- **Grok** (xAI)

---

**Built with ❤️ by the EudoraX Team**
