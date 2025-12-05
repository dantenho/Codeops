import os

import google.generativeai as genai
from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class GeminiAnalysisInput(NodeInput):
    content: str = Field(..., description="Content to analyze")
    prompt: str = Field(..., description="Analysis prompt")

class GeminiAnalysisOutput(NodeOutput):
    result: str = Field(..., description="Analysis result")

class GeminiAnalysisNode(NodeBase):
    """Node for generic Gemini analysis."""

    def execute(self, input_data: GeminiAnalysisInput) -> GeminiAnalysisOutput:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return GeminiAnalysisOutput(result="Mock Analysis Result (No API Key)")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        full_prompt = f"{input_data.prompt}\n\nContent:\n{input_data.content}"

        try:
            response = model.generate_content(full_prompt)
            return GeminiAnalysisOutput(result=response.text)
        except Exception as e:
            return GeminiAnalysisOutput(result=f"Error: {e}")
