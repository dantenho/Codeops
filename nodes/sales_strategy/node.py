import json
import os
from typing import Any, Dict, List

import google.generativeai as genai
from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class SalesStrategyInput(NodeInput):
    trends: List[Dict[str, Any]] = Field(..., description="Trend data")
    gas_price: float = Field(..., description="Current gas price")
    art_description: str = Field(..., description="Description of the generated art")

class SalesStrategyOutput(NodeOutput):
    listing_price_eth: float = Field(..., description="Recommended listing price")
    listing_duration_days: int = Field(..., description="Recommended duration")
    rationale: str = Field(..., description="Reasoning for the strategy")

class SalesStrategyNode(NodeBase):
    """Node for determining sales strategy using Gemini."""

    def execute(self, input_data: SalesStrategyInput) -> SalesStrategyOutput:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return SalesStrategyOutput(listing_price_eth=0.01, listing_duration_days=7, rationale="Default strategy (No API Key)")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Analyze the following market data to determine a sales strategy for an NFT.

        Trends: {input_data.trends}
        Current Gas Price: {input_data.gas_price} Gwei
        Art Description: {input_data.art_description}

        Recommend a listing price in ETH and duration in days. Provide a rationale.
        Format response as JSON: {{ "price": float, "duration": int, "rationale": "string" }}
        """

        try:
            response = model.generate_content(prompt)
            text = response.text
            # Clean markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text)

            return SalesStrategyOutput(
                listing_price_eth=float(data.get("price", 0.01)),
                listing_duration_days=int(data.get("duration", 7)),
                rationale=data.get("rationale", "AI generated strategy")
            )
        except Exception as e:
            print(f"Gemini Analysis failed: {e}")
            return SalesStrategyOutput(listing_price_eth=0.01, listing_duration_days=7, rationale=f"Fallback due to error: {e}")
