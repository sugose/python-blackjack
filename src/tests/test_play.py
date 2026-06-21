"""Tests for src/play.py — human session launcher CLI."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from src.table import Table


def _run_main(argv: list[str]) -> None:
    with patch.object(sys, "argv", ["src.play"] + argv):
        from src.play import main

        main()


@pytest.fixture(autouse=True)
def _patch_session(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("src.play.play_table_session", mock)
    return mock


def test_main_runs_with_valid_args(_patch_session):
    """Valid args launch a session — play_table_session called once with a Table instance."""
    with patch.object(sys, "argv", ["src.play"]):
        from src.play import main

        main()

    _patch_session.assert_called_once()
    args, kwargs = _patch_session.call_args
    assert isinstance(args[0], Table)


def test_invalid_deck_count_exits(monkeypatch, capsys):
    """Invalid deck count exits cleanly with sys.exit(1) and error message on stderr."""
    with patch.object(sys, "argv", ["src.play", "--decks", "3"]):
        with pytest.raises(SystemExit) as exc_info:
            from src.play import main

            main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
    assert "3" in captured.err


def test_invalid_hands_exits(capsys):
    """--hands 0 exits with sys.exit(1) and error message on stderr."""
    with patch.object(sys, "argv", ["src.play", "--hands", "0"]):
        with pytest.raises(SystemExit) as exc_info:
            from src.play import main

            main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
    assert "0" in captured.err


def test_invalid_bet_exits(capsys):
    """--bet 0 exits with sys.exit(1) and error message on stderr."""
    with patch.object(sys, "argv", ["src.play", "--bet", "0"]):
        with pytest.raises(SystemExit) as exc_info:
            from src.play import main

            main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
    assert "0" in captured.err


def test_negative_bet_exits(capsys):
    """--bet -5 exits with sys.exit(1) and error message on stderr."""
    with patch.object(sys, "argv", ["src.play", "--bet", "-5"]):
        with pytest.raises(SystemExit) as exc_info:
            from src.play import main

            main()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
    assert "-5" in captured.err


def test_default_args(_patch_session):
    """Default args: wallet=100.0, bet=1.0, decks=6, hands=10, name='Player'."""
    with patch.object(sys, "argv", ["src.play"]):
        from src.play import main

        main()

    args, kwargs = _patch_session.call_args
    table: Table = args[0]
    player = table.players[0]
    assert player.name == "Player"
    assert player.wallet == 100.0
    assert player.bet == 1.0
    assert table.numDecks == 6
    assert kwargs.get("max_hands") == 10


def test_valid_deck_counts(_patch_session):
    """All of {1, 2, 4, 6, 8} launch without error."""
    for decks in [1, 2, 4, 6, 8]:
        _patch_session.reset_mock()
        with patch.object(sys, "argv", ["src.play", "--decks", str(decks)]):
            from src.play import main

            main()
        _patch_session.assert_called_once()


def test_seed_passed_to_session(_patch_session):
    """play_table_session called with seed=42 when --seed 42 given."""
    with patch.object(sys, "argv", ["src.play", "--seed", "42"]):
        from src.play import main

        main()

    _, kwargs = _patch_session.call_args
    assert kwargs.get("seed") == 42


def test_max_hands_passed_to_session(_patch_session):
    """play_table_session called with max_hands=5 when --hands 5 given."""
    with patch.object(sys, "argv", ["src.play", "--hands", "5"]):
        from src.play import main

        main()

    _, kwargs = _patch_session.call_args
    assert kwargs.get("max_hands") == 5
