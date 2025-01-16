# agent/custom_llm.py

import json
import requests
from langchain.llms.base import LLM
from typing import Optional, List

class OllamaLLM(LLM):
    """
    A LangChain-compatible LLM wrapper for Ollama (local LLaMA-based models).
    Assumes Ollama is running on http://localhost:11411.
    """

    endpoint_url: str = "http://localhost:11411"
    model: str = "llama2-7b"  # or the name of your Ollama model
    temperature: float = 0.7

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
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error calling Ollama: {e}")

        output_lines = []
        for line in response.text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                line_data = json.loads(line)
                content = line_data.get("content", "")
                output_lines.append(content)
            except json.JSONDecodeError:
                # In case there's a stray line we can't parse as JSON
                output_lines.append(line)

        return "".join(output_lines)
