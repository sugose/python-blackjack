"""AIProvider protocol — the interface all providers must implement."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class AIProvider(Protocol):
    """Protocol for AI provider backends."""

    def query(self, context: str, prompt: str) -> str: ...
