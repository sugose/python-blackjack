"""Tests for src/main.py — entry point."""

from unittest.mock import patch

from src.main import main


def test_main_calls_play_session(tmp_path, monkeypatch) -> None:
    """main() delegates to play_session(), not play_hand_standalone()."""
    monkeypatch.chdir(tmp_path)
    with patch("src.main.play_session") as mock_play_session:
        main()
    mock_play_session.assert_called_once()


def test_main_does_not_call_play_hand_standalone(tmp_path, monkeypatch) -> None:
    """main() does not call play_hand_standalone() — that wrapper is not the entry point."""
    monkeypatch.chdir(tmp_path)
    with (
        patch("src.main.play_session"),
        patch("src.game.play_hand_standalone") as mock_standalone,
    ):
        main()
    mock_standalone.assert_not_called()
