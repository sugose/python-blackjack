"""Provider registry — instantiate providers by name from environment config."""

import os

from src.providers.base import AIProvider


def get_provider(name: str) -> AIProvider:
    """Instantiate and return a provider by name.

    Provider config is read from environment variables:
      ANTHROPIC_MODEL   — required for 'anthropic'
      OLLAMA_MODEL      — required for 'ollama'
      OLLAMA_BASE_URL   — optional for 'ollama', defaults to http://localhost:11434

    Raises ValueError for unknown provider names.
    Raises RuntimeError if required env vars are missing.
    """
    if name == "mock":
        from src.providers.mock import MockProvider

        return MockProvider()

    if name == "anthropic":
        model = os.environ.get("ANTHROPIC_MODEL")
        if not model:
            raise RuntimeError(
                "ANTHROPIC_MODEL environment variable is required for the anthropic provider"
            )
        from src.providers.anthropic import AnthropicProvider

        return AnthropicProvider(model=model)

    if name == "ollama":
        model = os.environ.get("OLLAMA_MODEL")
        if not model:
            raise RuntimeError(
                "OLLAMA_MODEL environment variable is required for the ollama provider"
            )
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        from src.providers.ollama import OllamaProvider

        return OllamaProvider(model=model, base_url=base_url)

    raise ValueError(f"Unknown provider: {name!r}. Known providers: anthropic, ollama, mock")
