"""MockProvider — deterministic responses for testing."""


class MockProvider:
    """Returns a fixed response for every query — no external dependencies."""

    def __init__(self, response: str = "stand") -> None:
        self._response = response

    def query(self, context: str, prompt: str) -> str:
        """Return the configured response regardless of input."""
        return self._response
