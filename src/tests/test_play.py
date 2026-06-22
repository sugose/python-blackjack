"""Tests for src/play.py — mixed-player table launcher CLI."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from src.table import Table


@pytest.fixture(autouse=True)
def _patch_session(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("src.play.play_table_session", mock)
    return mock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(argv: list[str]) -> None:
    """Run src.play.main() with the given argv."""
    with patch.object(sys, "argv", ["src.play"] + argv):
        from src.play import main

        main()


# ---------------------------------------------------------------------------
# Valid cases
# ---------------------------------------------------------------------------


def test_single_human_player(_patch_session):
    """Session launched with one human player — play_table_session called once with a Table."""
    with patch("builtins.input", return_value="stand"):
        _run(["--players", "Alice:human:100"])
    _patch_session.assert_called_once()
    args, _ = _patch_session.call_args
    assert isinstance(args[0], Table)
    assert len(args[0].players) == 1
    assert args[0].players[0].name == "Alice"


def test_two_player_mixed(_patch_session):
    """Table has two players with correct names, strategies, and wallets."""
    _run(["--players", "Alice:mirror:100", "Bot:hit:50"])
    args, _ = _patch_session.call_args
    table: Table = args[0]
    assert len(table.players) == 2
    assert table.players[0].name == "Alice"
    assert table.players[0].wallet == 100.0
    assert table.players[1].name == "Bot"
    assert table.players[1].wallet == 50.0


def test_all_strategy_names(_patch_session):
    """mirror, hit, stand, human all parse and construct without error."""
    with patch("builtins.input", return_value="stand"):
        _run(["--players", "A:mirror:10", "B:hit:10", "C:stand:10", "D:human:10"])
    _patch_session.assert_called_once()
    args, _ = _patch_session.call_args
    assert len(args[0].players) == 4


def test_seed_passed_to_session(_patch_session):
    """play_table_session called with seed=42 when --seed 42 given."""
    _run(["--players", "Bot:mirror:100", "--seed", "42"])
    _, kwargs = _patch_session.call_args
    assert kwargs.get("seed") == 42


def test_hands_passed_to_session(_patch_session):
    """play_table_session called with max_hands=5 when --hands 5 given."""
    _run(["--players", "Bot:mirror:100", "--hands", "5"])
    _, kwargs = _patch_session.call_args
    assert kwargs.get("max_hands") == 5


# ---------------------------------------------------------------------------
# Validation errors — exit 1
# ---------------------------------------------------------------------------


def test_missing_players_exits(capsys):
    """No --players flag → SystemExit(1) with error on stderr."""
    with pytest.raises(SystemExit) as exc:
        _run([])
    assert exc.value.code == 1
    assert "Error" in capsys.readouterr().err


def test_bad_spec_format_exits(capsys):
    """Spec with wrong number of parts → exit 1 naming the bad spec."""
    with pytest.raises(SystemExit) as exc:
        _run(["--players", "Alice:100"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error" in err
    assert "Alice:100" in err


def test_unknown_strategy_exits(capsys):
    """Unknown strategy name → exit 1 naming the bad value."""
    with pytest.raises(SystemExit) as exc:
        _run(["--players", "Alice:wizard:100"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error" in err
    assert "wizard" in err


def test_invalid_wallet_exits(capsys):
    """Wallet ≤ 0 → exit 1."""
    with pytest.raises(SystemExit) as exc:
        _run(["--players", "Alice:mirror:0"])
    assert exc.value.code == 1
    assert "Error" in capsys.readouterr().err


def test_duplicate_names_exits(capsys):
    """Two players with the same name → exit 1."""
    with pytest.raises(SystemExit) as exc:
        _run(["--players", "Alice:mirror:100", "Alice:hit:50"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error" in err
    assert "Alice" in err


def test_invalid_deck_count_exits(capsys):
    """--decks 3 → exit 1."""
    with pytest.raises(SystemExit) as exc:
        _run(["--players", "Bot:mirror:100", "--decks", "3"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error" in err
    assert "3" in err


def test_invalid_hands_exits(capsys):
    """--hands 0 → exit 1."""
    with pytest.raises(SystemExit) as exc:
        _run(["--players", "Bot:mirror:100", "--hands", "0"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Error" in err
    assert "0" in err
