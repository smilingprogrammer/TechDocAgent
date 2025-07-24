"""
llm.py
Module for LLM integration: calls Gemini API for documentation generation using the official google-genai library (v1.x+).
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"

def generate_documentation(prompt):
    """
    Call the Gemini API with the given prompt and return the generated documentation.
    Requires GOOGLE_API_KEY in environment variables.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )
    return response.text 