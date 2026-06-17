"""Tests for src/logger.py."""

import logging

import pytest

from src.logger import log_event


@pytest.mark.parametrize(
    "tag, message",
    [
        ("DECK", "Shuffled 52-card deck"),
        ("BET", "Player bets 1 UoM — wallet: 99 UoM"),
        ("DEAL", "Player dealt 7 of Hearts — hand value: 7"),
        ("HIT", "Player hits: 5 of Clubs — hand value: 15"),
        ("STAND", "Player stands on 19"),
        ("BUST", "Player busts with 23"),
        ("REVEAL", "Dealer reveals: King of Hearts — hand value: 17"),
        ("OUTCOME", "Player wins — player 20 beats dealer 17"),
        ("WALLET", "Player wallet: 101 UoM"),
        ("TABLE", "Player leaves — wallet reached 0 UoM"),
    ],
)
def test_log_event_emits_formatted_message(
    tag: str, message: str, caplog: pytest.LogCaptureFixture
) -> None:
    """log_event writes '[TAG] message' at INFO level."""
    with caplog.at_level(logging.INFO, logger="blackjack"):
        log_event(tag, message)
    assert f"[{tag}] {message}" in caplog.text


def test_log_event_uses_info_level(caplog: pytest.LogCaptureFixture) -> None:
    """log_event always logs at INFO level."""
    with caplog.at_level(logging.INFO, logger="blackjack"):
        log_event("DECK", "test")
    assert caplog.records[0].levelno == logging.INFO
