"""
Local Tools Integration Module.

This module provides unified access to all locally cloned GitHub tools:
- LangGraph: Workflow orchestration
- LangChain: LLM application framework
- CivitAI: Model downloader
- ComfyUI: Image generation
- Real-ESRGAN: Image upscaling
- Anime4KCPP: Anime upscaling
- Firecrawl: Web scraping
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Tools directory
TOOLS_DIR = Path(__file__).parent.parent.parent.parent / "tools"


class LocalToolsManager:
    """Manager for locally cloned GitHub tools."""

    TOOL_CONFIGS = {
        "langgraph": {
            "path": TOOLS_DIR / "langgraph",
            "python_path": "libs/langgraph/langgraph",
            "entry_module": "langgraph.graph",
            "description": "LangChain workflow orchestration"
        },
        "langchain": {
            "path": TOOLS_DIR / "langchain",
            "python_path": "libs/langchain/langchain",
            "entry_module": "langchain",
            "description": "LLM application framework"
        },
        "civitai": {
            "path": TOOLS_DIR / "civitai",
            "python_path": "",
            "entry_module": None,
            "description": "CivitAI model marketplace (TypeScript)"
        },
        "comfyui": {
            "path": TOOLS_DIR / "ComfyUI",
            "python_path": "",
            "entry_module": "main",
            "description": "Node-based image generation"
        },
        "real_esrgan": {
            "path": TOOLS_DIR / "Real-ESRGAN",
            "python_path": "",
            "entry_module": "inference_realesrgan",
            "description": "Real-world image restoration"
        },
        "anime4k": {
            "path": TOOLS_DIR / "Anime4KCPP",
            "python_path": "",
            "entry_module": None,
            "description": "Anime upscaling (C++)"
        },
        "firecrawl": {
            "path": TOOLS_DIR / "firecrawl",
            "python_path": "apps/python-sdk/firecrawl",
            "entry_module": "firecrawl",
            "description": "Web scraping and crawling"
        }
    }

    def __init__(self):
        self._loaded_tools: Dict[str, Any] = {}
        self._setup_paths()

    def _setup_paths(self):
        """Add tool paths to sys.path for imports."""
        for name, config in self.TOOL_CONFIGS.items():
            tool_path = config["path"]
            if tool_path.exists():
                # Add main path
                if str(tool_path) not in sys.path:
                    sys.path.insert(0, str(tool_path))

                # Add python subpath if specified
                if config["python_path"]:
                    py_path = tool_path / config["python_path"]
                    if py_path.exists() and str(py_path) not in sys.path:
                        sys.path.insert(0, str(py_path))

    def get_tool_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all local tools."""
        status = {}
        for name, config in self.TOOL_CONFIGS.items():
            tool_path = config["path"]
            status[name] = {
                "available": tool_path.exists(),
                "path": str(tool_path),
                "description": config["description"]
            }
        return status

    def is_available(self, tool_name: str) -> bool:
        """Check if a tool is available."""
        if tool_name not in self.TOOL_CONFIGS:
            return False
        return self.TOOL_CONFIGS[tool_name]["path"].exists()

    def get_tool_path(self, tool_name: str) -> Optional[Path]:
        """Get path to a tool."""
        if tool_name not in self.TOOL_CONFIGS:
            return None
        return self.TOOL_CONFIGS[tool_name]["path"]


# =============================================================================
# LANGGRAPH INTEGRATION
# =============================================================================

class LangGraphLocal:
    """Local LangGraph integration."""

    def __init__(self, manager: LocalToolsManager):
        self.manager = manager
        self._graph_module = None

    def load(self):
        """Load LangGraph from local source."""
        if not self.manager.is_available("langgraph"):
            raise ImportError("LangGraph not available locally")

        try:
            # Try local import first
            from langgraph.graph import END, StateGraph
            self._graph_module = StateGraph
            return StateGraph, END
        except ImportError:
            # Fallback to installed package
            from langgraph.graph import END, StateGraph
            return StateGraph, END

    def create_workflow(self, state_class):
        """Create a new workflow graph."""
        StateGraph, _ = self.load()
        return StateGraph(state_class)


# =============================================================================
# LANGCHAIN INTEGRATION
# =============================================================================

class LangChainLocal:
    """Local LangChain integration."""

    def __init__(self, manager: LocalToolsManager):
        self.manager = manager

    def get_chat_model(self, model_name: str = "gemini-pro"):
        """Get a chat model instance."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=model_name)
        except ImportError:
            print("Warning: langchain_google_genai not installed")
            return None

    def get_embeddings(self, model_name: str = "models/embedding-001"):
        """Get embeddings model."""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(model=model_name)
        except ImportError:
            from langchain.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings()

    def create_rag_chain(self, retriever, llm=None):
        """Create a RAG chain."""
        if llm is None:
            llm = self.get_chat_model()

        try:
            from langchain.chains import RetrievalQA
            return RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever
            )
        except Exception as e:
            print(f"Error creating RAG chain: {e}")
            return None


# =============================================================================
# COMFYUI INTEGRATION
# =============================================================================

class ComfyUILocal:
    """Local ComfyUI integration."""

    def __init__(self, manager: LocalToolsManager):
        self.manager = manager
        self.comfyui_path = manager.get_tool_path("comfyui")

    def get_api_url(self) -> str:
        """Get ComfyUI API URL."""
        return os.getenv("COMFYUI_API_URL", "http://127.0.0.1:8188")

    def load_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """Load a workflow JSON file."""
        import json
        with open(workflow_path, "r") as f:
            return json.load(f)

    def list_models(self) -> List[str]:
        """List available models in ComfyUI."""
        if not self.comfyui_path:
            return []

        models_dir = self.comfyui_path / "models" / "checkpoints"
        if not models_dir.exists():
            return []

        return [f.name for f in models_dir.glob("*.safetensors")]

    def list_loras(self) -> List[str]:
        """List available LoRAs."""
        if not self.comfyui_path:
            return []

        loras_dir = self.comfyui_path / "models" / "loras"
        if not loras_dir.exists():
            return []

        return [f.name for f in loras_dir.glob("*.safetensors")]


# =============================================================================
# REAL-ESRGAN INTEGRATION
# =============================================================================

class RealESRGANLocal:
    """Local Real-ESRGAN integration."""

    def __init__(self, manager: LocalToolsManager):
        self.manager = manager
        self.esrgan_path = manager.get_tool_path("real_esrgan")

    def get_inference_script(self) -> Optional[Path]:
        """Get path to inference script."""
        if not self.esrgan_path:
            return None
        return self.esrgan_path / "inference_realesrgan.py"

    def upscale(self, input_path: str, output_path: str = None, scale: int = 4) -> str:
        """Upscale an image."""
        import subprocess

        script = self.get_inference_script()
        if not script or not script.exists():
            raise FileNotFoundError("Real-ESRGAN inference script not found")

        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_upscaled{ext}"

        cmd = [
            sys.executable, str(script),
            "-i", input_path,
            "-o", output_path,
            "-s", str(scale)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Real-ESRGAN error: {result.stderr}")
            return input_path

        return output_path


# =============================================================================
# ANIME4K INTEGRATION
# =============================================================================

class Anime4KLocal:
    """Local Anime4KCPP integration."""

    def __init__(self, manager: LocalToolsManager):
        self.manager = manager
        self.anime4k_path = manager.get_tool_path("anime4k")

    def get_cli_binary(self) -> Optional[Path]:
        """Get path to CLI binary."""
        if not self.anime4k_path:
            return None

        # Check common binary locations
        for binary_name in ["Anime4KCPP_CLI.exe", "anime4kcpp", "Anime4KCPP_CLI"]:
            binary = self.anime4k_path / "build" / "bin" / binary_name
            if binary.exists():
                return binary

        return None

    def upscale(self, input_path: str, output_path: str = None) -> str:
        """Upscale using Anime4K."""
        import subprocess

        binary = self.get_cli_binary()
        if not binary:
            # Try pyanime4k fallback
            try:
                import pyanime4k
                a4k = pyanime4k.Anime4K()
                a4k.load_image(input_path)
                a4k.process()

                if output_path is None:
                    base, ext = os.path.splitext(input_path)
                    output_path = f"{base}_anime4k{ext}"

                a4k.save_image(output_path)
                return output_path
            except ImportError:
                print("Warning: Neither Anime4KCPP binary nor pyanime4k available")
                return input_path

        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_anime4k{ext}"

        cmd = [str(binary), "-i", input_path, "-o", output_path]
        subprocess.run(cmd, capture_output=True)
        return output_path


# =============================================================================
# FIRECRAWL INTEGRATION
# =============================================================================

class FirecrawlLocal:
    """Local Firecrawl integration."""

    def __init__(self, manager: LocalToolsManager):
        self.manager = manager
        self.firecrawl_path = manager.get_tool_path("firecrawl")

    def get_api_key(self) -> Optional[str]:
        """Get Firecrawl API key."""
        return os.getenv("FIRECRAWL_API_KEY")

    def scrape(self, url: str) -> Dict[str, Any]:
        """Scrape a URL using Firecrawl."""
        try:
            from firecrawl import FirecrawlApp

            api_key = self.get_api_key()
            if api_key:
                app = FirecrawlApp(api_key=api_key)
                return app.scrape_url(url)
            else:
                # Mock response if no API key
                return {"url": url, "content": "Mock content", "status": "no_api_key"}

        except ImportError:
            return {"url": url, "error": "firecrawl not installed"}

    def crawl(self, url: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Crawl a website."""
        try:
            from firecrawl import FirecrawlApp

            api_key = self.get_api_key()
            if api_key:
                app = FirecrawlApp(api_key=api_key)
                return app.crawl_url(url, params={"limit": max_pages})
            else:
                return [{"url": url, "status": "no_api_key"}]

        except ImportError:
            return [{"url": url, "error": "firecrawl not installed"}]


# =============================================================================
# CIVITAI INTEGRATION
# =============================================================================

class CivitAILocal:
    """Local CivitAI integration."""

    API_BASE = "https://civitai.com/api/v1"

    def __init__(self, manager: LocalToolsManager):
        self.manager = manager
        self.civitai_path = manager.get_tool_path("civitai")

    def search_models(self, query: str, model_type: str = "LORA") -> List[Dict[str, Any]]:
        """Search CivitAI for models."""
        import requests

        try:
            response = requests.get(
                f"{self.API_BASE}/models",
                params={"query": query, "types": model_type, "limit": 10}
            )

            if response.ok:
                return response.json().get("items", [])
            return []

        except Exception as e:
            print(f"CivitAI search error: {e}")
            return []

    def download_model(self, model_id: int, version_id: int, output_dir: str) -> Optional[str]:
        """Download a model from CivitAI."""
        import requests

        try:
            # Get model info
            response = requests.get(f"{self.API_BASE}/models/{model_id}")
            if not response.ok:
                return None

            model_data = response.json()
            version = next(
                (v for v in model_data.get("modelVersions", []) if v["id"] == version_id),
                None
            )

            if not version:
                return None

            # Download file
            file_info = version.get("files", [{}])[0]
            download_url = file_info.get("downloadUrl")

            if not download_url:
                return None

            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, file_info.get("name", f"model_{model_id}.safetensors"))

            print(f"Downloading {file_info.get('name')}...")

            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(output_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            return output_path

        except Exception as e:
            print(f"CivitAI download error: {e}")
            return None


# =============================================================================
# UNIFIED TOOLS FACADE
# =============================================================================

class LocalTools:
    """Unified facade for all local tools."""

    def __init__(self):
        self.manager = LocalToolsManager()

        # Initialize all integrations
        self.langgraph = LangGraphLocal(self.manager)
        self.langchain = LangChainLocal(self.manager)
        self.comfyui = ComfyUILocal(self.manager)
        self.real_esrgan = RealESRGANLocal(self.manager)
        self.anime4k = Anime4KLocal(self.manager)
        self.firecrawl = FirecrawlLocal(self.manager)
        self.civitai = CivitAILocal(self.manager)

    def status(self) -> Dict[str, Any]:
        """Get status of all tools."""
        return self.manager.get_tool_status()

    def available_tools(self) -> List[str]:
        """List available tools."""
        return [name for name, status in self.status().items() if status["available"]]


# Global instance
tools = LocalTools()


if __name__ == "__main__":
    print("Local Tools Status:")
    print("=" * 50)

    for name, status in tools.status().items():
        icon = "✅" if status["available"] else "❌"
        print(f"{icon} {name}: {status['description']}")

    print("\nAvailable:", tools.available_tools())
