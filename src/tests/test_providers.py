"""Tests for src/providers — AIProvider protocol and concrete implementations."""

import json
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from src.providers.base import AIProvider
from src.providers.mock import MockProvider
from src.providers.ollama import OllamaProvider
from src.providers.registry import get_provider

# ---------------------------------------------------------------------------
# MockProvider
# ---------------------------------------------------------------------------


def test_mock_returns_configured_response():
    """MockProvider(response='hit').query() returns 'hit'."""
    assert MockProvider(response="hit").query("ctx", "prompt") == "hit"


def test_mock_default_response():
    """MockProvider default response is 'stand'."""
    assert MockProvider().query("", "") == "stand"


def test_mock_satisfies_protocol():
    """MockProvider satisfies the AIProvider protocol."""
    assert isinstance(MockProvider(), AIProvider)


# ---------------------------------------------------------------------------
# AnthropicProvider
# ---------------------------------------------------------------------------


def _make_fake_anthropic(response_text: str = "stand") -> MagicMock:
    """Return a fake anthropic module with a usable Anthropic client."""
    fake_anthropic = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]
    fake_anthropic.Anthropic.return_value.messages.create.return_value = mock_message
    return fake_anthropic


def test_anthropic_satisfies_protocol():
    """AnthropicProvider satisfies the AIProvider protocol."""
    import importlib
    import sys

    fake_anthropic = _make_fake_anthropic()
    with patch.dict(sys.modules, {"anthropic": fake_anthropic}):
        import src.providers.anthropic as mod

        importlib.reload(mod)
        assert isinstance(mod.AnthropicProvider(model="x"), AIProvider)


def test_anthropic_import_error():
    """AnthropicProvider raises ImportError when anthropic SDK is not installed."""
    import importlib
    import sys

    with patch.dict(sys.modules, {"anthropic": None}):
        import src.providers.anthropic as mod

        importlib.reload(mod)
        with pytest.raises(ImportError, match="anthropic package is required"):
            mod.AnthropicProvider(model="claude-3-haiku-20240307")


def test_anthropic_query():
    """AnthropicProvider.query() sends combined context+prompt and returns text."""
    import importlib
    import sys

    fake_anthropic = _make_fake_anthropic("hit")
    with patch.dict(sys.modules, {"anthropic": fake_anthropic}):
        import src.providers.anthropic as mod

        importlib.reload(mod)
        provider = mod.AnthropicProvider(model="claude-3-haiku-20240307")

    mock_client = provider._client
    result = provider.query("context text", "what to do?")

    assert result == "hit"
    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-3-haiku-20240307"
    assert call_kwargs["max_tokens"] == 256
    combined = call_kwargs["messages"][0]["content"]
    assert "context text" in combined
    assert "what to do?" in combined


# ---------------------------------------------------------------------------
# OllamaProvider
# ---------------------------------------------------------------------------


def test_ollama_satisfies_protocol():
    """OllamaProvider satisfies the AIProvider protocol."""
    assert isinstance(OllamaProvider(model="llama3"), AIProvider)


def _make_urlopen_response(data: dict):
    """Return a mock context manager yielding a BytesIO of JSON data."""
    body = json.dumps(data).encode()
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=BytesIO(body))
    cm.__exit__ = MagicMock(return_value=False)
    return cm


def test_ollama_query():
    """OllamaProvider.query() POSTs to /api/generate and returns the 'response' field."""
    provider = OllamaProvider(model="llama3")
    response_data = {"response": "stand", "done": True}

    with patch(
        "urllib.request.urlopen", return_value=_make_urlopen_response(response_data)
    ) as mock_open:
        result = provider.query("ctx", "prompt")

    assert result == "stand"
    mock_open.assert_called_once()
    request_arg = mock_open.call_args.args[0]
    assert request_arg.full_url == "http://localhost:11434/api/generate"
    payload = json.loads(request_arg.data)
    assert payload["model"] == "llama3"
    assert payload["stream"] is False
    assert "ctx" in payload["prompt"]
    assert "prompt" in payload["prompt"]


def test_ollama_http_error():
    """OllamaProvider raises RuntimeError with status code on HTTP error."""
    provider = OllamaProvider(model="llama3")
    http_err = urllib.error.HTTPError(
        url="http://localhost:11434/api/generate", code=404, msg="Not Found", hdrs=None, fp=None
    )

    with patch("urllib.request.urlopen", side_effect=http_err):
        with pytest.raises(RuntimeError, match="404"):
            provider.query("ctx", "prompt")


def test_ollama_connection_error():
    """OllamaProvider raises RuntimeError on connection failure."""
    provider = OllamaProvider(model="llama3")
    url_err = urllib.error.URLError(reason="Connection refused")

    with patch("urllib.request.urlopen", side_effect=url_err):
        with pytest.raises(RuntimeError):
            provider.query("ctx", "prompt")


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_registry_mock():
    """get_provider('mock') returns a MockProvider instance."""
    assert isinstance(get_provider("mock"), MockProvider)


def test_registry_anthropic(monkeypatch):
    """get_provider('anthropic') reads ANTHROPIC_MODEL and returns AnthropicProvider."""
    import importlib
    import sys

    fake_anthropic = _make_fake_anthropic()
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
    with patch.dict(sys.modules, {"anthropic": fake_anthropic}):
        import src.providers.anthropic as mod

        importlib.reload(mod)
        import src.providers.registry as reg_mod

        importlib.reload(reg_mod)
        provider = reg_mod.get_provider("anthropic")
    assert isinstance(provider, mod.AnthropicProvider)


def test_registry_anthropic_missing_model(monkeypatch):
    """get_provider('anthropic') raises RuntimeError when ANTHROPIC_MODEL is unset."""
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_MODEL"):
        get_provider("anthropic")


def test_registry_ollama(monkeypatch):
    """get_provider('ollama') reads OLLAMA_MODEL and returns OllamaProvider."""
    monkeypatch.setenv("OLLAMA_MODEL", "llama3")
    provider = get_provider("ollama")
    assert isinstance(provider, OllamaProvider)


def test_registry_ollama_missing_model(monkeypatch):
    """get_provider('ollama') raises RuntimeError when OLLAMA_MODEL is unset."""
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    with pytest.raises(RuntimeError, match="OLLAMA_MODEL"):
        get_provider("ollama")


def test_registry_unknown_provider():
    """get_provider('grok') raises ValueError with the name in the message."""
    with pytest.raises(ValueError, match="grok"):
        get_provider("grok")
