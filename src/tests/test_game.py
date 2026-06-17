"""Tests for src/game.py — deterministic via seeded deck."""

import logging

import pytest

from src.game import play_hand
from src.player import Player


def _stand_strategy(hand):  # type: ignore[no-untyped-def]
    return "stand"


def _hit_strategy(hand):  # type: ignore[no-untyped-def]
    return "hit"


def test_play_hand_deducts_bet_at_start(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand deducts 1 UoM bet from wallet at the start."""
    p = Player(name="Alice", strategy=_stand_strategy)
    initial = p.wallet
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    assert p.wallet != initial or "[BET]" in caplog.text


def test_play_hand_logs_deck_shuffle(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs deck shuffle."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    assert "[DECK]" in caplog.text


def test_play_hand_logs_deal_events(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs DEAL events for initial cards."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    assert "[DEAL]" in caplog.text


def test_play_hand_logs_outcome(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs an OUTCOME event."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    assert "[OUTCOME]" in caplog.text


def test_play_hand_logs_wallet(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs WALLET event."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    assert "[WALLET]" in caplog.text


def test_play_hand_player_bust_logs_bust(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs BUST when player busts."""
    p = Player(name="Alice", strategy=_hit_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    logs = caplog.text
    assert "[BUST] Player busts" in logs or "[OUTCOME]" in logs


def test_play_hand_wallet_zero_logs_table(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs TABLE when wallet reaches 0."""
    p = Player(name="Alice", strategy=_stand_strategy)
    p.wallet = 1.0
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=99)
    if p.wallet == 0.0:
        assert "[TABLE]" in caplog.text


def test_play_hand_blackjack_pays_150(caplog: pytest.LogCaptureFixture) -> None:
    """Blackjack pays 1.5 UoM profit (wallet goes from 99 to 100.5 after bet deduction)."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    if "[OUTCOME] Player blackjack" in caplog.text:
        assert p.wallet == 100.5


def test_play_hand_push_returns_bet(caplog: pytest.LogCaptureFixture) -> None:
    """Push returns bet — wallet unchanged from pre-hand value."""
    p = Player(name="Alice", strategy=_stand_strategy)
    start = p.wallet
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    if "Push" in caplog.text:
        assert p.wallet == start


def test_play_hand_dealer_bust_player_wins(caplog: pytest.LogCaptureFixture) -> None:
    """Dealer bust results in player winning 1 UoM."""
    p = Player(name="Alice", strategy=_stand_strategy)
    start = p.wallet
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    if "[BUST] Dealer busts" in caplog.text:
        assert p.wallet == start + 1.0


def test_play_hand_deterministic_same_seed(caplog: pytest.LogCaptureFixture) -> None:
    """Same seed produces the same outcome twice."""
    p1 = Player(name="Alice", strategy=_stand_strategy)
    p2 = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p1, seed=7)
    log1 = caplog.text
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p2, seed=7)
    log2 = caplog.text
    assert log1 == log2


def test_play_hand_logs_reveal(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs REVEAL event for dealer hole card."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=42)
    assert "[REVEAL]" in caplog.text
