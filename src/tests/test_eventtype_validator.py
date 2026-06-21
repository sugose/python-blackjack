"""CI validator — asserts every eventType literal in GameEvent(...) calls is in the known-valid set.

Uses the ast module to parse source files so string literals inside GameEvent(eventType=...)
keyword arguments are extracted reliably without regex.
"""

import ast
from pathlib import Path

KNOWN_EVENT_TYPES = {
    # Currently used (TPS Section 9)
    "SessionOpened",
    "SessionClosed",
    "HandStarted",
    "ShoeShuffled",
    "CutCardReached",
    "BetPlaced",
    "CardDealt",
    "CardDrawn",
    "StandDeclared",
    "HandBust",
    "HoleCardRevealed",
    "HandResolved",
    "PayoutMade",
    "WalletUpdated",
    "WalletEmpty",
    "PlayerLeft",
    "TableOpened",
    "TableClosed",
    "PlayerSeated",
    # Reserved (future PBIs — TPS Section 9)
    "SplitTaken",
    "DoubleDown",
    "PlayerJoined",
    "SitOut",
    "PlayerBooted",
}

_SRC_ROOT = Path(__file__).parent.parent
_TESTS_DIR = _SRC_ROOT / "tests"


def _collect_eventtype_literals(source_root: Path) -> list[tuple[str, int, str]]:
    """Return (file, line, eventType) for every GameEvent(eventType=<str>) call found."""
    results: list[tuple[str, int, str]] = []
    for path in sorted(source_root.rglob("*.py")):
        if path.is_relative_to(_TESTS_DIR):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            is_game_event = (isinstance(func, ast.Name) and func.id == "GameEvent") or (
                isinstance(func, ast.Attribute) and func.attr == "GameEvent"
            )
            if not is_game_event:
                continue
            for kw in node.keywords:
                if kw.arg == "eventType" and isinstance(kw.value.value, str):
                    results.append((str(path), kw.value.lineno, kw.value.value))
    return results


class TestEventTypeValidator:
    def test_known_event_types_set_is_not_empty(self) -> None:
        """Sanity check — the reference set must be populated."""
        assert len(KNOWN_EVENT_TYPES) > 0

    def test_all_eventtype_literals_are_known(self) -> None:
        """Every eventType literal in GameEvent(...) calls under src/ must be known."""
        hits = _collect_eventtype_literals(_SRC_ROOT)
        unknown = [
            f"{path}:{line} — '{et}'" for path, line, et in hits if et not in KNOWN_EVENT_TYPES
        ]
        assert not unknown, (
            "Unknown eventType(s) found — add to KNOWN_EVENT_TYPES or fix the source:\n"
            + "\n".join(unknown)
        )

    def test_validator_catches_unknown_eventtype(self, tmp_path: Path) -> None:
        """The scanner must detect an unknown eventType in a synthesised source file."""
        fake_src = tmp_path / "fake_module.py"
        fake_src.write_text(
            "from src.logger import GameEvent\n"
            'e = GameEvent(eventType="UnknownFakeEvent", sessionId="s", data={})\n',
            encoding="utf-8",
        )
        hits = _collect_eventtype_literals(tmp_path)
        unknown = [et for _, _, et in hits if et not in KNOWN_EVENT_TYPES]
        assert "UnknownFakeEvent" in unknown
