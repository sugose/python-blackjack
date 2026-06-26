"""AnthropicProvider — wraps the Anthropic SDK."""


class AnthropicProvider:
    """Queries Claude models via the Anthropic SDK."""

    def __init__(self, model: str, api_key: str | None = None) -> None:
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package is required for AnthropicProvider — pip install anthropic"
            )
        self._model = model
        self._client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def query(self, context: str, prompt: str) -> str:
        """Send context and prompt as a single user message; return the text response."""
        message = self._client.messages.create(
            model=self._model,
            max_tokens=256,
            messages=[{"role": "user", "content": f"{context}\n\n{prompt}"}],
        )
        return message.content[0].text
