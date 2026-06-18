"""Structured event logger — emits GameEvent to JSONL and human-readable format."""

import json
import logging
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

_logger = logging.getLogger("blackjack")


@dataclass
class GameEvent:
    """A structured game event."""

    eventType: str
    sessionId: str
    data: dict
    handId: str | None = None
    actor: str | None = None
    eventId: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )


def _hrf(event: GameEvent) -> str:
    """Render a GameEvent as a human-readable one-liner."""
    parts = [f"[{event.eventType}]"]
    parts.append(f"sess:{event.sessionId[-8:]}")
    if event.handId:
        parts.append(f"hand:{event.handId[-8:]}")
    parts.append(f"evt:{event.eventId[-8:]}")
    if event.actor:
        parts.append(f"actor:{event.actor}")
    message = event.data.get("message")
    if message is None:
        try:
            message = json.dumps(event.data)
        except TypeError:
            message = repr(event.data)
    return " | ".join(parts) + f" — {message}"


def emit_event(event: GameEvent, session_file: Path) -> None:
    """Write event to JSONL file and emit HRF to stdout via logging."""
    # JSONL write — never crash the game on logging failure
    try:
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with session_file.open("a", encoding="utf-8") as f:
            payload = {
                "eventId": event.eventId,
                "eventType": event.eventType,
                "timestamp": event.timestamp,
                "sessionId": event.sessionId,
                "data": event.data,
            }
            if event.handId is not None:
                payload["handId"] = event.handId
            if event.actor is not None:
                payload["actor"] = event.actor
            f.write(json.dumps(payload) + "\n")
    except Exception as exc:
        warnings.warn(f"JSONL write failed: {exc}", stacklevel=2)

    # HRF to stdout
    _logger.info(_hrf(event))
