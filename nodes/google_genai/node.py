"""
Google GenAI (Gemini) Node.

This module provides the GoogleGenAINode for dynamic code generation
and AI-assisted coding using Google's Gemini model.

Typical usage:
    node = GoogleGenAINode(name="genai")
    output = node.execute(GoogleGenAIInput(prompt="Write a Python function"))
"""

from codeops.core.node import NodeBase, NodeInput, NodeOutput
from pydantic import Field


class GoogleGenAIInput(NodeInput):
    """Input schema for GoogleGenAINode.

    Attributes:
        prompt: The prompt for code/logic generation.
    """
    prompt: str = Field(..., description="Prompt for code/logic generation")


class GoogleGenAIOutput(NodeOutput):
    """Output schema for GoogleGenAINode.

    Attributes:
        content: The generated code or text content.
    """
    content: str = Field(default="", description="Generated content")


class GoogleGenAINode(NodeBase):
    """Node for Google Gemini Code Generation.

    This node interfaces with Google's Gemini API to generate Python code,
    JSON configurations, or other dynamic logic based on prompts.

    Role: Code Sentry - provides AI-assisted coding and self-healing.

    Example:
        >>> node = GoogleGenAINode(name="genai")
        >>> output = node.execute(GoogleGenAIInput(
        ...     prompt="Write a function to validate email addresses"
        ... ))
        >>> print(output.content[:50])
        'def validate_email(email: str) -> bool:\n    ...'
    """

    def execute(self, input_data: GoogleGenAIInput) -> GoogleGenAIOutput:
        """Execute Gemini code generation.

        Args:
            input_data: GoogleGenAIInput with generation prompt.

        Returns:
            GoogleGenAIOutput with generated code/content.
        """
        import os

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not set. Returning mock.")
            return GoogleGenAIOutput(content="# Mock Code\nprint('Hello World')")

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')

            response = model.generate_content(input_data.prompt)
            return GoogleGenAIOutput(content=response.text)

        except ImportError:
            print("Warning: google-generativeai not installed")
            return GoogleGenAIOutput(content="# Error: google-generativeai not installed")
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            return GoogleGenAIOutput(content=f"# Error: {e}")
