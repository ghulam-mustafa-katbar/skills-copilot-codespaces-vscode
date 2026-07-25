"""AI provider integrations."""

import json
from typing import Any

import requests
from loguru import logger


class OllamaProvider:
    """Metadata generation through locally hosted Ollama."""

    def __init__(self, base_url: str, model: str, timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> dict[str, Any] | None:
        """Call Ollama and return parsed JSON metadata if available."""

        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            body = response.json()
            raw_response = body.get("response", "")
            return json.loads(raw_response) if raw_response else None
        except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
            logger.warning("Ollama generation failed: {}", exc)
            return None
