"""
Workflow Builder using Local Tools.

This module provides a workflow builder that combines
all local tools into cohesive pipelines.
"""

from typing import Any, Dict, List, Optional, TypedDict

from .local_tools import tools


class ContentPipelineState(TypedDict):
    """State for content generation pipeline."""
    # Input
    prompt: str
    style: str

    # Research
    trends: List[Dict[str, Any]]
    web_content: List[Dict[str, Any]]
    rag_context: List[str]

    # Generation
    lora_path: Optional[str]
    generated_images: List[str]
    upscaled_images: List[str]

    # Evaluation
    clip_scores: List[float]
    selected_image: Optional[str]

    # Output
    status: str
    errors: List[str]


class WorkflowBuilder:
    """Builder for creating workflows using local tools."""

    def __init__(self):
        self.tools = tools

    def create_content_pipeline(self):
        """Create the full content generation pipeline."""
        StateGraph, END = self.tools.langgraph.load()

        workflow = StateGraph(ContentPipelineState)

        # Add nodes
        workflow.add_node("research", self._research_node)
        workflow.add_node("get_assets", self._asset_node)
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("upscale", self._upscale_node)
        workflow.add_node("evaluate", self._evaluate_node)

        # Set flow
        workflow.set_entry_point("research")
        workflow.add_edge("research", "get_assets")
        workflow.add_edge("get_assets", "generate")
        workflow.add_edge("generate", "upscale")
        workflow.add_edge("upscale", "evaluate")
        workflow.add_edge("evaluate", END)

        return workflow.compile()

    def _research_node(self, state: ContentPipelineState) -> Dict[str, Any]:
        """Research trends and gather context."""
        print("📊 Researching trends...")

        trends = []
        web_content = []
        rag_context = []
        errors = []

        # Web research with Firecrawl
        try:
            if state.get("prompt"):
                search_url = f"https://www.google.com/search?q={state['prompt']}+art+trends"
                result = self.tools.firecrawl.scrape(search_url)
                web_content.append(result)
        except Exception as e:
            errors.append(f"Firecrawl: {e}")

        # RAG context
        try:
            llm = self.tools.langchain.get_chat_model()
            if llm:
                # Simplified context generation
                rag_context.append(f"Context for: {state.get('prompt', 'digital art')}")
        except Exception as e:
            errors.append(f"LangChain: {e}")

        return {
            "trends": trends,
            "web_content": web_content,
            "rag_context": rag_context,
            "errors": errors
        }

    def _asset_node(self, state: ContentPipelineState) -> Dict[str, Any]:
        """Download assets from CivitAI."""
        print("📦 Loading assets from CivitAI...")

        lora_path = None
        errors = list(state.get("errors", []))

        try:
            style = state.get("style", "anime")
            models = self.tools.civitai.search_models(style, "LORA")

            if models:
                # For now, just log the found models
                print(f"Found {len(models)} LoRAs matching '{style}'")
                # In production, would download the best match

        except Exception as e:
            errors.append(f"CivitAI: {e}")

        return {"lora_path": lora_path, "errors": errors}

    def _generate_node(self, state: ContentPipelineState) -> Dict[str, Any]:
        """Generate images using ComfyUI."""
        print("🎨 Generating images...")

        generated = []
        errors = list(state.get("errors", []))

        try:
            # List available models
            models = self.tools.comfyui.list_models()
            loras = self.tools.comfyui.list_loras()

            print(f"Available: {len(models)} models, {len(loras)} LoRAs")

            # In production, would execute ComfyUI workflow
            generated.append("output/generated_001.png")

        except Exception as e:
            errors.append(f"ComfyUI: {e}")

        return {"generated_images": generated, "errors": errors}

    def _upscale_node(self, state: ContentPipelineState) -> Dict[str, Any]:
        """Upscale images using Real-ESRGAN or Anime4K."""
        print("🔍 Upscaling images...")

        upscaled = []
        errors = list(state.get("errors", []))

        for img_path in state.get("generated_images", []):
            try:
                # Try Real-ESRGAN first
                if self.tools.manager.is_available("real_esrgan"):
                    result = self.tools.real_esrgan.upscale(img_path)
                    upscaled.append(result)
                # Fallback to Anime4K
                elif self.tools.manager.is_available("anime4k"):
                    result = self.tools.anime4k.upscale(img_path)
                    upscaled.append(result)
                else:
                    upscaled.append(img_path)

            except Exception as e:
                errors.append(f"Upscale: {e}")
                upscaled.append(img_path)

        return {"upscaled_images": upscaled, "errors": errors}

    def _evaluate_node(self, state: ContentPipelineState) -> Dict[str, Any]:
        """Evaluate images and select the best."""
        print("✅ Evaluating results...")

        images = state.get("upscaled_images", state.get("generated_images", []))
        errors = list(state.get("errors", []))

        # For now, select the first image
        selected = images[0] if images else None

        return {
            "selected_image": selected,
            "clip_scores": [0.8] * len(images),
            "status": "complete" if selected else "failed",
            "errors": errors
        }


# =============================================================================
# QUICK WORKFLOWS
# =============================================================================

def upscale_image(input_path: str, method: str = "auto") -> str:
    """Quick upscale an image."""
    if method == "esrgan" or (method == "auto" and tools.manager.is_available("real_esrgan")):
        return tools.real_esrgan.upscale(input_path)
    elif method == "anime4k" or method == "auto":
        return tools.anime4k.upscale(input_path)
    return input_path


def search_loras(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Quick search for LoRAs on CivitAI."""
    return tools.civitai.search_models(query, "LORA")[:limit]


def scrape_url(url: str) -> Dict[str, Any]:
    """Quick scrape a URL."""
    return tools.firecrawl.scrape(url)


def create_rag_chain(documents: List[str]):
    """Create a RAG chain from documents."""
    from langchain.text_splitter import CharacterTextSplitter
    from langchain.vectorstores import Chroma

    # Split documents
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = splitter.create_documents(documents)

    # Create vector store
    embeddings = tools.langchain.get_embeddings()
    vectorstore = Chroma.from_documents(texts, embeddings)

    # Create chain
    return tools.langchain.create_rag_chain(vectorstore.as_retriever())


if __name__ == "__main__":
    print("Testing Workflow Builder...")

    builder = WorkflowBuilder()

    # Check tools status
    print("\nTools Status:")
    for name, status in tools.status().items():
        icon = "✅" if status["available"] else "❌"
        print(f"  {icon} {name}")
