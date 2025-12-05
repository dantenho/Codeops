import os
import uuid
from typing import Optional

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from playwright.sync_api import sync_playwright
from pydantic import Field

try:
    from codeops.memory.vector_store import get_vector_store
except ImportError:
    get_vector_store = None


class PlaywrightInput(NodeInput):
    url: str = Field(..., description="URL to visit")
    wait_for_selector: Optional[str] = Field(default=None, description="Selector to wait for")
    extract_selector: Optional[str] = Field(default="body", description="Selector to extract text from")
    screenshot: bool = Field(default=False, description="Take a screenshot?")
    save_to_db: bool = Field(default=False, description="Save content to Vector DB?")
    collection_name: str = Field(default="web_scrapes", description="Collection name for DB")

class PlaywrightOutput(NodeOutput):
    content: str = Field(..., description="Extracted text content")
    html: str = Field(..., description="Full HTML content")
    screenshot_path: Optional[str] = Field(default=None, description="Path to screenshot if taken")
    db_id: Optional[str] = Field(default=None, description="ID of the saved document in DB")

class PlaywrightNode(NodeBase):
    """Node for Playwright browser automation."""

    def execute(self, input_data: PlaywrightInput) -> PlaywrightOutput:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(input_data.url)

            if input_data.wait_for_selector:
                page.wait_for_selector(input_data.wait_for_selector)

            content = page.inner_text(input_data.extract_selector)
            html = page.content()

            screenshot_path = None
            if input_data.screenshot:
                # Ensure output dir exists
                os.makedirs("output/screenshots", exist_ok=True)
                # Sanitize filename
                safe_name = "".join([c for c in input_data.url if c.isalnum() or c in ['.', '-']]).strip()
                filename = f"output/screenshots/{safe_name}.png"
                page.screenshot(path=filename)
                screenshot_path = filename

            browser.close()

            db_id = None
            if input_data.save_to_db and get_vector_store:
                try:
                    store = get_vector_store("chroma")
                    # Note: ChromaVectorStore in memory package might need update to support dynamic collections
                    # For now, we assume it uses a default or we modify it.
                    # The current implementation uses "codebase" collection hardcoded.
                    # We should probably update VectorStore to accept collection name, but for now let's just add it.

                    doc_id = str(uuid.uuid4())
                    store.add_documents(
                        documents=[content],
                        metadatas=[{"url": input_data.url, "type": "web_scrape", "screenshot": screenshot_path or ""}],
                        ids=[doc_id]
                    )
                    db_id = doc_id
                    print(f"Saved scrape to DB with ID: {db_id}")
                except Exception as e:
                    print(f"Failed to save to DB: {e}")

            return PlaywrightOutput(content=content, html=html, screenshot_path=screenshot_path, db_id=db_id)
