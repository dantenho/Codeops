from typing import Any, Dict, List

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class SocialMediaInput(NodeInput):
    platform: str = Field(default="all", description="Platform to scrape (reddit, youtube, all)")
    keywords: List[str] = Field(default=["nft", "digital art", "generative art"], description="Keywords to search")

class SocialMediaOutput(NodeOutput):
    trends: List[Dict[str, Any]] = Field(..., description="List of trending items")

class SocialMediaNode(NodeBase):
    """Node for fetching social media trends."""

    def execute(self, input_data: SocialMediaInput) -> SocialMediaOutput:
        trends = []

        # Mock implementation for now as we don't have real API keys set up in this env
        # In production, this would use praw, google-api-python-client, etc.

        print(f"Fetching trends from {input_data.platform} for {input_data.keywords}")

        if input_data.platform in ["reddit", "all"]:
            trends.append({"source": "reddit", "title": "New AI Art Style Trending", "score": 1500})
            trends.append({"source": "reddit", "title": "CryptoPunks making a comeback?", "score": 800})

        if input_data.platform in ["youtube", "all"]:
            trends.append({"source": "youtube", "title": "Top 10 NFT Projects 2025", "views": 50000})

        return SocialMediaOutput(trends=trends)
