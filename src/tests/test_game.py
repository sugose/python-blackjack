"""Tests for src/game.py — deterministic via seeded deck.

Seed reference (stand strategy unless noted):
  seed=0  → dealer bust          (player wins +1 UoM)
  seed=2  → dealer wins          (player loses -1 UoM)
  seed=19 → push                 (wallet unchanged)
  seed=49 → player blackjack only (pays 3:2, +1.5 UoM)
  seed=498 → both blackjack      (push, wallet unchanged)
"""

import logging

import pytest

from src.game import play_hand
from src.hand import Hand
from src.player import Player


def _stand_strategy(hand: Hand) -> str:
    return "stand"


def _hit_strategy(hand: Hand) -> str:
    return "hit"


def test_play_hand_deducts_bet_at_start(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs BET event and deducts 1 UoM."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=2)
    assert "[BET]" in caplog.text
    assert p.wallet == 99.0


def test_play_hand_logs_deck_shuffle(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs deck shuffle."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=2)
    assert "[DECK] Shuffled 52-card deck" in caplog.text


def test_play_hand_logs_deal_events(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs DEAL events for initial cards."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=2)
    assert "[DEAL]" in caplog.text


def test_play_hand_logs_outcome(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs an OUTCOME event."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=2)
    assert "[OUTCOME]" in caplog.text


def test_play_hand_logs_wallet(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs WALLET event."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=2)
    assert "[WALLET]" in caplog.text


def test_play_hand_player_bust_logs_bust(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs BUST when player always hits until bust."""
    p = Player(name="Alice", strategy=_hit_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=2)
    assert "[BUST] Player busts" in caplog.text
    assert "[OUTCOME]" not in caplog.text


def test_play_hand_wallet_zero_logs_table(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs TABLE when wallet reaches 0 after a loss."""
    p = Player(name="Alice", strategy=_stand_strategy)
    p.wallet = 1.0
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=2)
    assert p.wallet == 0.0
    assert "[TABLE] Player leaves — wallet reached 0 UoM" in caplog.text


def test_play_hand_player_blackjack_only_pays_3_to_2(caplog: pytest.LogCaptureFixture) -> None:
    """Player blackjack (dealer does not have blackjack) pays 3:2 — wallet: 100 → 101.5."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=49)
    assert "[OUTCOME] Player blackjack — pays 3:2" in caplog.text
    assert p.wallet == 101.5


def test_play_hand_both_blackjack_is_push(caplog: pytest.LogCaptureFixture) -> None:
    """Both player and dealer have blackjack — outcome is a push, wallet unchanged."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=498)
    assert "[OUTCOME] Push — both have blackjack" in caplog.text
    assert p.wallet == 100.0


def test_play_hand_push_returns_bet(caplog: pytest.LogCaptureFixture) -> None:
    """Push returns the bet — wallet is unchanged at 100 UoM."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=19)
    assert "Push" in caplog.text
    assert p.wallet == 100.0


def test_play_hand_dealer_bust_player_wins(caplog: pytest.LogCaptureFixture) -> None:
    """Dealer bust results in player winning 1 UoM — wallet goes from 100 to 101."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=0)
    assert "[BUST] Dealer busts" in caplog.text
    assert p.wallet == 101.0


def test_play_hand_invalid_strategy_raises() -> None:
    """Strategy returning an unknown action raises ValueError."""

    def bad_strategy(hand: Hand) -> str:
        return "double"

    p = Player(name="Alice", strategy=bad_strategy)
    with pytest.raises(ValueError, match="Unknown strategy action"):
        play_hand(p, seed=2)


def test_play_hand_deterministic_same_seed(caplog: pytest.LogCaptureFixture) -> None:
    """Same seed produces identical log output twice."""
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


def test_play_hand_dealer_blackjack_only_player_loses(caplog: pytest.LogCaptureFixture) -> None:
    """Dealer blackjack (player does not have blackjack) — player loses bet, wallet: 99."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=9)
    assert "[REVEAL]" in caplog.text
    assert "[OUTCOME] Dealer blackjack — player loses" in caplog.text
    assert p.wallet == 99.0


def test_play_hand_logs_reveal(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs REVEAL event for dealer hole card (non-blackjack hand)."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, seed=2)
    assert "[REVEAL]" in caplog.text
