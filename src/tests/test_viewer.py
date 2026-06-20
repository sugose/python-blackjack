"""Tests for src/viewer.py — JSONL viewer CLI (ICE-2)."""

import json
from pathlib import Path
from typing import Any

import pytest

from src.viewer import main, match_event, parse_filter

# Fixed UUIDs for deterministic assertions
SESSION_ID = "00000000-0000-0000-0000-aabb00000001"
SESSION_ID_2 = "00000000-0000-0000-0000-aabb00000002"
HAND_ID = "00000000-0000-0000-0000-ccdd00000001"
EVENT_ID_1 = "00000000-0000-0000-0000-eeee00000001"
EVENT_ID_2 = "00000000-0000-0000-0000-eeee00000002"
EVENT_ID_3 = "00000000-0000-0000-0000-eeee00000003"


def _make_event(
    event_type: str,
    session_id: str = SESSION_ID,
    event_id: str = EVENT_ID_1,
    actor: str | None = None,
    hand_id: str | None = None,
    timestamp: str = "2024-01-01T00:00:00+00:00",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    e: dict[str, Any] = {
        "eventId": event_id,
        "eventType": event_type,
        "timestamp": timestamp,
        "sessionId": session_id,
        "data": data or {"message": f"{event_type} occurred"},
    }
    if hand_id is not None:
        e["handId"] = hand_id
    if actor is not None:
        e["actor"] = actor
    return e


def _write_jsonl(path: Path, events: list[dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")


# --- Invocation ---


def test_no_args_prints_help_and_exits_0(capsys: pytest.CaptureFixture) -> None:
    """No arguments → prints help to stdout and exits 0."""
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "usage" in out.lower()


def test_version_exits_0(capsys: pytest.CaptureFixture) -> None:
    """--version prints version string and exits 0."""
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_filter_only_no_files_prints_help_and_exits_0(capsys: pytest.CaptureFixture) -> None:
    """--filter with no files → prints help and exits 0."""
    with pytest.raises(SystemExit) as exc:
        main(["--filter", "eventType=BetPlaced"])
    assert exc.value.code == 0


# --- Basic output ---


def test_single_file_no_filter_outputs_all_events(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """All events in a file are printed as HRF one-liners when no filter is set."""
    events = [
        _make_event("SessionOpened", event_id=EVENT_ID_1, timestamp="2024-01-01T00:00:00+00:00"),
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_2,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
    ]
    f = tmp_path / "session.jsonl"
    _write_jsonl(f, events)
    main([str(f)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 2
    assert "[SessionOpened]" in lines[0]
    assert "[BetPlaced]" in lines[1]


def test_hrf_output_format_matches_logger_hrf(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """HRF output includes sess:, evt:, hand:, actor: parts per logger._hrf format."""
    event = _make_event(
        "BetPlaced",
        session_id=SESSION_ID,
        event_id=EVENT_ID_1,
        hand_id=HAND_ID,
        actor="Alice",
        data={"message": "bet placed"},
    )
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, [event])
    main([str(f)])
    out = capsys.readouterr().out.strip()
    assert "[BetPlaced]" in out
    assert f"sess:{SESSION_ID[-8:]}" in out
    assert f"hand:{HAND_ID[-8:]}" in out
    assert f"evt:{EVENT_ID_1[-8:]}" in out
    assert "actor:Alice" in out
    assert "bet placed" in out


def test_session_level_event_hrf_omits_hand_and_actor(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Session-level events (no handId) omit hand: and actor: from HRF output."""
    event = _make_event("SessionOpened", session_id=SESSION_ID, event_id=EVENT_ID_1)
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, [event])
    main([str(f)])
    out = capsys.readouterr().out.strip()
    assert "hand:" not in out
    assert "actor:" not in out


def test_no_matching_events_outputs_nothing(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """When no events match the filter, nothing is printed to stdout."""
    events = [_make_event("SessionOpened")]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "eventType=BetPlaced"])
    out = capsys.readouterr().out.strip()
    assert out == ""


# --- Filter: equality ---


def test_filter_event_type_equality(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """eventType=BetPlaced returns only BetPlaced events."""
    events = [
        _make_event("SessionOpened", event_id=EVENT_ID_1),
        _make_event("BetPlaced", event_id=EVENT_ID_2, hand_id=HAND_ID, actor="Alice"),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "eventType=BetPlaced"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "[BetPlaced]" in lines[0]


def test_filter_actor_player_matches_non_dealer(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """actor=player matches any event where actor is not 'Dealer'."""
    events = [
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_1,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        _make_event(
            "CardDealt",
            event_id=EVENT_ID_2,
            hand_id=HAND_ID,
            actor="Dealer",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "actor=player"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "actor:Alice" in lines[0]


def test_filter_actor_dealer_matches_dealer_only(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """actor=dealer matches only events where actor is 'Dealer' (case-insensitive)."""
    events = [
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_1,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        _make_event(
            "CardDealt",
            event_id=EVENT_ID_2,
            hand_id=HAND_ID,
            actor="Dealer",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "actor=dealer"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "actor:Dealer" in lines[0]


def test_filter_actor_literal_match(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """actor=Alice matches only events with actor 'Alice'."""
    events = [
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_1,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_2,
            hand_id=HAND_ID,
            actor="Bob",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "actor=Alice"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "actor:Alice" in lines[0]


def test_filter_uuid_suffix_match_session_id(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """sessionId=<suffix> matches events whose sessionId ends with the given suffix."""
    events = [
        _make_event(
            "SessionOpened",
            session_id=SESSION_ID,
            event_id=EVENT_ID_1,
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        _make_event(
            "SessionOpened",
            session_id=SESSION_ID_2,
            event_id=EVENT_ID_2,
            timestamp="2024-01-01T00:00:01+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    # SESSION_ID ends with "00000001", SESSION_ID_2 ends with "00000002"
    main([str(f), "--filter", "sessionId=00000001"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert f"sess:{SESSION_ID[-8:]}" in lines[0]


def test_filter_uuid_suffix_match_hand_id(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """handId=<suffix> matches events whose handId ends with the given suffix."""
    hand_id_2 = "00000000-0000-0000-0000-ccdd00000002"
    events = [
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_1,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_2,
            hand_id=hand_id_2,
            actor="Bob",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "handId=00000001"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "actor:Alice" in lines[0]


# --- Filter: operators ---


def test_filter_contains_operator(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """~= operator matches events where the field value contains the given string."""
    events = [
        _make_event("BetPlaced", event_id=EVENT_ID_1, timestamp="2024-01-01T00:00:00+00:00"),
        _make_event("CardDealt", event_id=EVENT_ID_2, timestamp="2024-01-01T00:00:01+00:00"),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "eventType~=Bet"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "[BetPlaced]" in lines[0]


def test_filter_not_equals_operator(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """!= operator excludes events where the field value matches."""
    events = [
        _make_event("SessionOpened", event_id=EVENT_ID_1, timestamp="2024-01-01T00:00:00+00:00"),
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_2,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "eventType!=SessionOpened"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "[BetPlaced]" in lines[0]


# --- Filter: logical operators ---


def test_filter_and_logic(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """AND requires both conditions to be true."""
    events = [
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_1,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_2,
            hand_id=HAND_ID,
            actor="Dealer",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
        _make_event(
            "CardDealt",
            event_id=EVENT_ID_3,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:02+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "eventType=BetPlaced AND actor=player"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "[BetPlaced]" in lines[0]
    assert "actor:Alice" in lines[0]


def test_filter_or_logic(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """OR requires at least one condition to be true."""
    events = [
        _make_event("SessionOpened", event_id=EVENT_ID_1, timestamp="2024-01-01T00:00:00+00:00"),
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_2,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
        _make_event(
            "HandResolved",
            event_id=EVENT_ID_3,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:02+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "eventType=SessionOpened OR eventType=BetPlaced"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 2
    assert "[SessionOpened]" in lines[0]
    assert "[BetPlaced]" in lines[1]


def test_filter_parentheses_grouping(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Parentheses correctly group sub-expressions."""
    events = [
        _make_event(
            "CardDealt",
            event_id=EVENT_ID_1,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:00+00:00",
        ),
        _make_event(
            "CardDealt",
            event_id=EVENT_ID_2,
            hand_id=HAND_ID,
            actor="Dealer",
            timestamp="2024-01-01T00:00:01+00:00",
        ),
        _make_event(
            "BetPlaced",
            event_id=EVENT_ID_3,
            hand_id=HAND_ID,
            actor="Alice",
            timestamp="2024-01-01T00:00:02+00:00",
        ),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "(eventType=CardDealt OR eventType=BetPlaced) AND actor=dealer"])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 1
    assert "[CardDealt]" in lines[0]
    assert "actor:Dealer" in lines[0]


# --- Filter: case-insensitivity ---


def test_filter_field_name_case_insensitive(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Filter field names are case-insensitive (ACTOR, Actor, actor all work)."""
    events = [
        _make_event("BetPlaced", event_id=EVENT_ID_1, hand_id=HAND_ID, actor="Dealer"),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "ACTOR=dealer"])
    out = capsys.readouterr().out.strip()
    assert "[BetPlaced]" in out


def test_filter_value_case_insensitive(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Filter values are case-insensitive (BetPlaced, betplaced both match)."""
    events = [
        _make_event("BetPlaced", event_id=EVENT_ID_1, hand_id=HAND_ID, actor="Alice"),
    ]
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, events)
    main([str(f), "--filter", "eventType=betplaced"])
    out = capsys.readouterr().out.strip()
    assert "[BetPlaced]" in out


# --- Error handling ---


def test_unknown_filter_field_exits_nonzero(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Unknown filter field prints error, prints help, and exits non-zero."""
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, [_make_event("BetPlaced")])
    with pytest.raises(SystemExit) as exc:
        main([str(f), "--filter", "unknownField=foo"])
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "unknownField" in err or "unknown" in err.lower()


def test_player_id_filter_exits_nonzero_reserved_field(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """playerId is reserved and not implemented in v1 — exits non-zero."""
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, [_make_event("BetPlaced")])
    with pytest.raises(SystemExit) as exc:
        main([str(f), "--filter", "playerId=abc"])
    assert exc.value.code != 0


def test_invalid_filter_expression_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Malformed filter expression prints error and exits non-zero."""
    f = tmp_path / "s.jsonl"
    _write_jsonl(f, [_make_event("BetPlaced")])
    with pytest.raises(SystemExit) as exc:
        main([str(f), "--filter", "AND AND AND"])
    assert exc.value.code != 0


def test_missing_file_exits_nonzero(capsys: pytest.CaptureFixture) -> None:
    """Non-existent literal file path exits non-zero."""
    with pytest.raises(SystemExit) as exc:
        main(["/no/such/file.jsonl"])
    assert exc.value.code != 0


def test_unresolvable_glob_exits_nonzero(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Glob pattern that matches nothing exits non-zero."""
    with pytest.raises(SystemExit) as exc:
        main([str(tmp_path / "*.nosuchext")])
    assert exc.value.code != 0


# --- Multi-file merging ---


def test_multiple_files_merged_chronologically(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Events from multiple files are merged and sorted by timestamp."""
    f1 = tmp_path / "a.jsonl"
    f2 = tmp_path / "b.jsonl"
    _write_jsonl(
        f1,
        [
            _make_event(
                "SessionOpened", event_id=EVENT_ID_1, timestamp="2024-01-01T00:00:02+00:00"
            ),
        ],
    )
    _write_jsonl(
        f2,
        [
            _make_event(
                "BetPlaced",
                event_id=EVENT_ID_2,
                hand_id=HAND_ID,
                actor="Alice",
                timestamp="2024-01-01T00:00:01+00:00",
            ),
        ],
    )
    main([str(f1), str(f2)])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 2
    # BetPlaced (00:01) must come before SessionOpened (00:02)
    assert "[BetPlaced]" in lines[0]
    assert "[SessionOpened]" in lines[1]


def test_glob_expansion_matches_multiple_files(
    tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Glob pattern expands to multiple files and outputs events from all of them."""
    f1 = tmp_path / "sess1.jsonl"
    f2 = tmp_path / "sess2.jsonl"
    _write_jsonl(
        f1,
        [_make_event("SessionOpened", event_id=EVENT_ID_1, timestamp="2024-01-01T00:00:00+00:00")],
    )
    _write_jsonl(
        f2,
        [
            _make_event(
                "BetPlaced",
                event_id=EVENT_ID_2,
                hand_id=HAND_ID,
                actor="Alice",
                timestamp="2024-01-01T00:00:01+00:00",
            )
        ],
    )
    pattern = str(tmp_path / "*.jsonl")
    main([pattern])
    out = capsys.readouterr().out
    lines = [ln for ln in out.splitlines() if ln.strip()]
    assert len(lines) == 2


# --- Unit tests for parse_filter / match_event ---


def test_parse_filter_returns_cmp_node() -> None:
    """parse_filter returns a CMP tuple for a simple comparison."""
    node = parse_filter("eventType=BetPlaced")
    assert node[0] == "CMP"
    assert node[1] == "eventtype"
    assert node[2] == "="
    assert node[3] == "BetPlaced"


def test_parse_filter_and_node() -> None:
    """parse_filter returns an AND node for A AND B."""
    node = parse_filter("eventType=BetPlaced AND actor=player")
    assert node[0] == "AND"


def test_parse_filter_or_node() -> None:
    """parse_filter returns an OR node for A OR B."""
    node = parse_filter("eventType=BetPlaced OR eventType=CardDealt")
    assert node[0] == "OR"


def test_parse_filter_raises_on_unknown_field() -> None:
    """parse_filter raises ValueError for an unknown field."""
    with pytest.raises(ValueError, match="Unknown filter field"):
        parse_filter("noSuchField=foo")


def test_parse_filter_raises_on_empty_expression() -> None:
    """parse_filter raises ValueError for an empty string."""
    with pytest.raises(ValueError):
        parse_filter("")


@pytest.mark.parametrize(
    "actor,event_actor,expected",
    [
        ("player", "Alice", True),
        ("player", "Dealer", False),
        ("dealer", "Dealer", True),
        ("dealer", "Alice", False),
        ("Alice", "Alice", True),
        ("Alice", "Bob", False),
    ],
)
def test_match_event_actor_semantics(actor: str, event_actor: str, expected: bool) -> None:
    """actor= filter respects player/dealer abstraction and literal match."""
    event = _make_event("BetPlaced", actor=event_actor, hand_id=HAND_ID)
    node = parse_filter(f"actor={actor}")
    assert match_event(event, node) is expected


def test_match_event_missing_field_does_not_match() -> None:
    """Filtering on handId when event has no handId returns False."""
    event = _make_event("SessionOpened")  # no handId
    node = parse_filter("handId=00000001")
    assert match_event(event, node) is False


def test_match_event_contains_operator() -> None:
    """~= operator performs case-insensitive substring match."""
    event = _make_event("BetPlaced")
    assert match_event(event, parse_filter("eventType~=bet")) is True
    assert match_event(event, parse_filter("eventType~=Card")) is False


def test_match_event_not_equals_operator() -> None:
    """!= operator excludes exact matches."""
    event = _make_event("BetPlaced")
    assert match_event(event, parse_filter("eventType!=BetPlaced")) is False
    assert match_event(event, parse_filter("eventType!=SessionOpened")) is True
