# agent/src/custom_llm.py
import json
import requests
from langchain.llms.base import LLM
from typing import Optional, List
from src.config import Config  # New configuration file for modularity

class OllamaLLM(LLM):
    """
    A LangChain-compatible LLM wrapper for Ollama.
    """

    def __init__(self, endpoint_url=None, model=None, temperature=None):
        self.endpoint_url = endpoint_url or Config.OLLAMA_URL
        self.model = model or Config.OLLAMA_MODEL
        self.temperature = temperature or Config.TEMPERATURE

    @property
    def _llm_type(self) -> str:
        return "ollama_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        payload = {
            "prompt": prompt,
            "model": self.model,
            "temperature": self.temperature
        }
        try:
            response = requests.post(f"{self.endpoint_url}/generate", json=payload, timeout=300)
            response.raise_for_status()
            return self._parse_response(response.text)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error calling Ollama: {e}")

    def _parse_response(self, response_text: str) -> str:
        output_lines = []
        for line in response_text.splitlines():
            try:
                line_data = json.loads(line.strip())
                content = line_data.get("content", "")
                output_lines.append(content)
            except json.JSONDecodeError:
                output_lines.append(line)
        return "".join(output_lines)
