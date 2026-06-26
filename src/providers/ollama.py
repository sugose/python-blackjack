"""OllamaProvider — queries a local Ollama instance via HTTP (stdlib only)."""

import json
import urllib.error
import urllib.request


class OllamaProvider:
    """Calls a local Ollama instance; no external SDK required."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")

    def query(self, context: str, prompt: str) -> str:
        """POST to /api/generate and return the 'response' field from the JSON reply."""
        url = f"{self._base_url}/api/generate"
        payload = json.dumps(
            {"model": self._model, "prompt": f"{context}\n\n{prompt}", "stream": False}
        ).encode()
        request = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(request) as resp:
                data = json.loads(resp.read())
                return data["response"]
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Ollama request failed with HTTP {exc.code}: {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Ollama connection failed: {exc.reason}") from exc
