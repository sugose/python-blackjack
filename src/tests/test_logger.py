"""Tests for src/logger.py — GameEvent dataclass and emit_event()."""

import json
import logging
import warnings
from pathlib import Path
from unittest.mock import patch

import pytest

from src.logger import GameEvent, emit_event

SESSION_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
HAND_ID = "11111111-2222-3333-4444-555555555555"
ACTOR = "Alice"


def _make_session_event() -> GameEvent:
    return GameEvent(
        eventType="OPEN",
        sessionId=SESSION_ID,
        data={"message": "Session started"},
    )


def _make_hand_event() -> GameEvent:
    return GameEvent(
        eventType="BET",
        sessionId=SESSION_ID,
        handId=HAND_ID,
        actor=ACTOR,
        data={"bet": 1, "message": "Player bets 1 UoM — wallet: 99 UoM"},
    )


def test_emit_event_creates_jsonl_file(tmp_path: Path) -> None:
    """emit_event creates the JSONL file at the correct path."""
    session_file = tmp_path / "sessions" / "test.jsonl"
    emit_event(_make_hand_event(), session_file)
    assert session_file.exists()


def test_emit_event_writes_valid_json(tmp_path: Path) -> None:
    """emit_event writes a valid JSON object per line."""
    session_file = tmp_path / "test.jsonl"
    emit_event(_make_hand_event(), session_file)
    lines = session_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert isinstance(json.loads(lines[0]), dict)


def test_emit_event_json_contains_required_fields(tmp_path: Path) -> None:
    """JSON object contains eventId, eventType, timestamp, sessionId, data."""
    session_file = tmp_path / "test.jsonl"
    emit_event(_make_hand_event(), session_file)
    parsed = json.loads(session_file.read_text(encoding="utf-8").strip())
    for field in ("eventId", "eventType", "timestamp", "sessionId", "data"):
        assert field in parsed, f"Missing required field: {field}"


def test_emit_event_json_omits_hand_id_when_none(tmp_path: Path) -> None:
    """handId is omitted from JSON when not provided."""
    session_file = tmp_path / "test.jsonl"
    event = _make_session_event()
    assert event.handId is None
    emit_event(event, session_file)
    assert "handId" not in json.loads(session_file.read_text(encoding="utf-8").strip())


def test_emit_event_json_omits_actor_when_none(tmp_path: Path) -> None:
    """actor is omitted from JSON when not provided."""
    session_file = tmp_path / "test.jsonl"
    event = _make_session_event()
    assert event.actor is None
    emit_event(event, session_file)
    assert "actor" not in json.loads(session_file.read_text(encoding="utf-8").strip())


def test_emit_event_json_includes_hand_id_when_provided(tmp_path: Path) -> None:
    """handId is present in JSON when provided."""
    session_file = tmp_path / "test.jsonl"
    emit_event(_make_hand_event(), session_file)
    parsed = json.loads(session_file.read_text(encoding="utf-8").strip())
    assert parsed["handId"] == HAND_ID


def test_emit_event_json_includes_actor_when_provided(tmp_path: Path) -> None:
    """actor is present in JSON when provided."""
    session_file = tmp_path / "test.jsonl"
    emit_event(_make_hand_event(), session_file)
    parsed = json.loads(session_file.read_text(encoding="utf-8").strip())
    assert parsed["actor"] == ACTOR


def test_emit_event_hrf_format_hand_level(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """HRF one-liner includes sess, hand, evt, actor for hand-level events."""
    session_file = tmp_path / "test.jsonl"
    with caplog.at_level(logging.INFO, logger="blackjack"):
        emit_event(_make_hand_event(), session_file)
    assert "[BET]" in caplog.text
    assert f"sess:{SESSION_ID[-8:]}" in caplog.text
    assert f"hand:{HAND_ID[-8:]}" in caplog.text
    assert "evt:" in caplog.text
    assert f"actor:{ACTOR}" in caplog.text
    assert "Player bets 1 UoM — wallet: 99 UoM" in caplog.text


def test_emit_event_hrf_format_session_level(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """HRF one-liner omits hand and actor for session-level events."""
    session_file = tmp_path / "test.jsonl"
    with caplog.at_level(logging.INFO, logger="blackjack"):
        emit_event(_make_session_event(), session_file)
    assert "[OPEN]" in caplog.text
    assert f"sess:{SESSION_ID[-8:]}" in caplog.text
    assert "hand:" not in caplog.text
    assert "actor:" not in caplog.text
    assert "Session started" in caplog.text


def test_emit_event_jsonl_failure_warns_not_raises(tmp_path: Path) -> None:
    """JSONL write failure emits warning and does not raise."""
    session_file = tmp_path / "test.jsonl"
    with patch("pathlib.Path.open", side_effect=OSError("disk full")):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            emit_event(_make_hand_event(), session_file)
    assert len(caught) == 1
    assert "JSONL write failed" in str(caught[0].message)


def test_hrf_non_serializable_data_does_not_raise(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """HRF rendering does not raise when data contains non-JSON-serialisable values."""
    session_file = tmp_path / "test.jsonl"
    event = GameEvent(
        eventType="DEBUG",
        sessionId=SESSION_ID,
        data={"obj": object()},  # no "message" key; object() is not JSON-serialisable
    )
    with caplog.at_level(logging.INFO, logger="blackjack"):
        emit_event(event, session_file)
    assert "[DEBUG]" in caplog.text


def test_hrf_session_level_event_with_actor_omits_actor_from_hrf(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Session-level event (handId=None) with actor set must NOT include actor: in HRF."""
    session_file = tmp_path / "test.jsonl"
    event = GameEvent(
        eventType="LEAVE",
        sessionId=SESSION_ID,
        actor=ACTOR,  # actor is set, but handId is None — should be omitted from HRF
        data={"message": "Player leaves — no funds"},
    )
    assert event.handId is None
    with caplog.at_level(logging.INFO, logger="blackjack"):
        emit_event(event, session_file)
    assert "[LEAVE]" in caplog.text
    assert "actor:" not in caplog.text
