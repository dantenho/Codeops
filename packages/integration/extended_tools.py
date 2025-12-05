"""
Extended Local Tools Integration.

Adds support for newly downloaded repositories:
- Playwright: Browser automation
- ChromaDB: Vector database
- Neo4j: Graph database
- Google GenAI: Gemini API
- CLIP: Vision-language model
- ViT/timm: Vision Transformers
- OpenPose: Pose estimation
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Base tools directory
TOOLS_DIR = Path(__file__).parent.parent.parent.parent / "tools"


# =============================================================================
# PLAYWRIGHT INTEGRATION
# =============================================================================

class PlaywrightLocal:
    """Playwright browser automation integration."""

    def __init__(self):
        self.path = TOOLS_DIR / "playwright"
        self._browser = None

    @property
    def available(self) -> bool:
        return self.path.exists()

    async def launch_browser(self, headless: bool = True):
        """Launch a browser instance."""
        from playwright.async_api import async_playwright

        pw = await async_playwright().start()
        self._browser = await pw.chromium.launch(headless=headless)
        return self._browser

    async def screenshot(self, url: str, output_path: str) -> str:
        """Take a screenshot of a URL."""
        if not self._browser:
            await self.launch_browser()

        page = await self._browser.new_page()
        await page.goto(url)
        await page.screenshot(path=output_path, full_page=True)
        await page.close()

        return output_path

    async def scrape_content(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL."""
        if not self._browser:
            await self.launch_browser()

        page = await self._browser.new_page()
        await page.goto(url)

        content = {
            "url": url,
            "title": await page.title(),
            "text": await page.inner_text("body"),
            "html": await page.content()
        }

        await page.close()
        return content


# =============================================================================
# CHROMADB INTEGRATION
# =============================================================================

class ChromaDBLocal:
    """ChromaDB vector database integration."""

    def __init__(self, persist_dir: str = "./chroma_db"):
        self.path = TOOLS_DIR / "chromadb"
        self.persist_dir = persist_dir
        self._client = None

    @property
    def available(self) -> bool:
        return self.path.exists()

    def get_client(self):
        """Get or create ChromaDB client."""
        if self._client is None:
            import chromadb
            from chromadb.config import Settings

            self._client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(allow_reset=True)
            )
        return self._client

    def get_or_create_collection(self, name: str, embedding_function=None):
        """Get or create a collection."""
        client = self.get_client()
        return client.get_or_create_collection(
            name=name,
            embedding_function=embedding_function
        )

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict] = None,
        ids: List[str] = None
    ):
        """Add documents to a collection."""
        collection = self.get_or_create_collection(collection_name)

        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        collection.add(
            documents=documents,
            metadatas=metadatas or [{} for _ in documents],
            ids=ids
        )

        return ids

    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Query a collection."""
        collection = self.get_or_create_collection(collection_name)
        return collection.query(query_texts=[query_text], n_results=n_results)


# =============================================================================
# NEO4J INTEGRATION
# =============================================================================

class Neo4jLocal:
    """Neo4j graph database integration."""

    def __init__(self, uri: str = "bolt://localhost:7687", auth: tuple = ("neo4j", "password")):
        self.path = TOOLS_DIR / "neo4j"
        self.uri = uri
        self.auth = auth
        self._driver = None

    @property
    def available(self) -> bool:
        return self.path.exists()

    def get_driver(self):
        """Get or create Neo4j driver."""
        if self._driver is None:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(self.uri, auth=self.auth)
        return self._driver

    def run_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """Run a Cypher query."""
        driver = self.get_driver()
        with driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def create_node(self, label: str, properties: Dict) -> Dict:
        """Create a node."""
        query = f"CREATE (n:{label} $props) RETURN n"
        results = self.run_query(query, {"props": properties})
        return results[0] if results else {}

    def create_relationship(
        self,
        from_label: str,
        from_props: Dict,
        to_label: str,
        to_props: Dict,
        rel_type: str
    ):
        """Create a relationship between nodes."""
        query = f"""
        MATCH (a:{from_label}), (b:{to_label})
        WHERE a.id = $from_id AND b.id = $to_id
        CREATE (a)-[r:{rel_type}]->(b)
        RETURN r
        """
        return self.run_query(query, {
            "from_id": from_props.get("id"),
            "to_id": to_props.get("id")
        })


# =============================================================================
# GOOGLE GENAI INTEGRATION
# =============================================================================

class GoogleGenAILocal:
    """Google Generative AI (Gemini) integration."""

    def __init__(self):
        self.path = TOOLS_DIR / "google-genai"
        self._model = None

    @property
    def available(self) -> bool:
        return self.path.exists()

    def configure(self, api_key: str = None):
        """Configure the API."""
        import google.generativeai as genai

        key = api_key or os.getenv("GOOGLE_API_KEY")
        if key:
            genai.configure(api_key=key)

    def get_model(self, model_name: str = "gemini-pro"):
        """Get a generative model."""
        import google.generativeai as genai

        self.configure()
        return genai.GenerativeModel(model_name)

    def generate(self, prompt: str, model: str = "gemini-pro") -> str:
        """Generate content."""
        model = self.get_model(model)
        response = model.generate_content(prompt)
        return response.text

    def chat(self, messages: List[Dict[str, str]], model: str = "gemini-pro"):
        """Start a chat session."""
        genai_model = self.get_model(model)
        chat = genai_model.start_chat()

        responses = []
        for msg in messages:
            if msg.get("role") == "user":
                response = chat.send_message(msg["content"])
                responses.append({"role": "assistant", "content": response.text})

        return responses

    def embed(self, text: str, model: str = "models/embedding-001") -> List[float]:
        """Generate embeddings."""
        import google.generativeai as genai

        self.configure()
        result = genai.embed_content(model=model, content=text)
        return result["embedding"]


# =============================================================================
# CLIP INTEGRATION
# =============================================================================

class CLIPLocal:
    """OpenAI CLIP integration for vision-language tasks."""

    def __init__(self):
        self.path = TOOLS_DIR / "clip"
        self._model = None
        self._preprocess = None

    @property
    def available(self) -> bool:
        return self.path.exists()

    def load_model(self, model_name: str = "ViT-B/32"):
        """Load CLIP model."""
        if self.path.exists():
            sys.path.insert(0, str(self.path))

        import clip
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model, self._preprocess = clip.load(model_name, device=device)

        return self._model

    def encode_image(self, image_path: str) -> List[float]:
        """Encode an image."""
        import torch
        from PIL import Image

        if self._model is None:
            self.load_model()

        device = "cuda" if torch.cuda.is_available() else "cpu"
        image = self._preprocess(Image.open(image_path)).unsqueeze(0).to(device)

        with torch.no_grad():
            features = self._model.encode_image(image)

        return features.cpu().numpy().tolist()[0]

    def encode_text(self, text: str) -> List[float]:
        """Encode text."""
        import clip
        import torch

        if self._model is None:
            self.load_model()

        device = "cuda" if torch.cuda.is_available() else "cpu"
        tokens = clip.tokenize([text]).to(device)

        with torch.no_grad():
            features = self._model.encode_text(tokens)

        return features.cpu().numpy().tolist()[0]

    def similarity(self, image_path: str, texts: List[str]) -> List[float]:
        """Calculate similarity between image and texts."""
        import clip
        import torch
        from PIL import Image

        if self._model is None:
            self.load_model()

        device = "cuda" if torch.cuda.is_available() else "cpu"

        image = self._preprocess(Image.open(image_path)).unsqueeze(0).to(device)
        text_tokens = clip.tokenize(texts).to(device)

        with torch.no_grad():
            image_features = self._model.encode_image(image)
            text_features = self._model.encode_text(text_tokens)

            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            similarity = (image_features @ text_features.T).softmax(dim=-1)

        return similarity.cpu().numpy().tolist()[0]


# =============================================================================
# OPENPOSE INTEGRATION
# =============================================================================

class OpenPoseLocal:
    """OpenPose pose estimation integration."""

    def __init__(self):
        self.path = TOOLS_DIR / "openpose"

    @property
    def available(self) -> bool:
        return self.path.exists()

    def get_model_path(self) -> Optional[Path]:
        """Get path to OpenPose models."""
        models_dir = self.path / "models"
        return models_dir if models_dir.exists() else None

    def estimate_pose(self, image_path: str) -> Dict[str, Any]:
        """Estimate pose from image (placeholder - needs OpenPose build)."""
        # OpenPose requires C++ build, this is a placeholder
        return {
            "status": "placeholder",
            "message": "OpenPose requires native build",
            "image": image_path
        }


# =============================================================================
# UNIFIED EXTENDED TOOLS
# =============================================================================

class ExtendedTools:
    """Extended tools facade including new repositories."""

    def __init__(self):
        self.playwright = PlaywrightLocal()
        self.chromadb = ChromaDBLocal()
        self.neo4j = Neo4jLocal()
        self.genai = GoogleGenAILocal()
        self.clip = CLIPLocal()
        self.openpose = OpenPoseLocal()

    def status(self) -> Dict[str, bool]:
        """Get status of all extended tools."""
        return {
            "playwright": self.playwright.available,
            "chromadb": self.chromadb.available,
            "neo4j": self.neo4j.available,
            "google_genai": self.genai.available,
            "clip": self.clip.available,
            "openpose": self.openpose.available
        }


# Global instance
extended_tools = ExtendedTools()


if __name__ == "__main__":
    print("Extended Tools Status:")
    print("=" * 50)
    for name, available in extended_tools.status().items():
        icon = "✅" if available else "❌"
        print(f"  {icon} {name}")
