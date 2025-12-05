import os
from typing import Any, Dict, List

import requests
from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class NFTTrendInput(NodeInput):
    chain: str = Field(default="ethereum", description="Chain to check trends for")
    limit: int = Field(default=10, description="Number of collections to fetch")

class NFTTrendOutput(NodeOutput):
    trends: List[Dict[str, Any]] = Field(..., description="List of trending collections")

class NFTTrendNode(NodeBase):
    """Node for fetching NFT trends."""

    def execute(self, input_data: NFTTrendInput) -> NFTTrendOutput:
        api_key = os.getenv("OPENSEA_API_KEY")
        if not api_key:
            # Fallback to mock data or public endpoint if available
            print("Warning: OPENSEA_API_KEY not found. Returning mock data.")
            return NFTTrendOutput(trends=[
                {"name": "Mock Collection 1", "volume": 100, "slug": "mock-1"},
                {"name": "Mock Collection 2", "volume": 50, "slug": "mock-2"}
            ])

        # Note: Endpoint might vary based on API version
        url = f"https://api.opensea.io/api/v2/collections?chain={input_data.chain}&limit={input_data.limit}"
        headers = {
            "accept": "application/json",
            "x-api-key": api_key
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return NFTTrendOutput(trends=data.get('collections', []))
            else:
                print(f"Error fetching trends: {response.status_code} - {response.text}")
                return NFTTrendOutput(trends=[])
        except Exception as e:
            print(f"Exception fetching trends: {e}")
            return NFTTrendOutput(trends=[])
