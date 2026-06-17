"""Tests for src/player.py."""

import pytest

from src.cards import Card
from src.hand import Hand
from src.player import Player


def _make_hand(value: int) -> Hand:
    """Return a Hand whose value equals `value` using 2s and a filler."""
    twos = value // 2
    cards = [Card("2", "Hearts")] * twos
    if value % 2:
        cards.append(Card("Ace", "Spades"))
        for _ in range(twos):
            cards.append(Card("2", "Hearts"))
        cards = [Card("Ace", "Spades")] + [Card("2", "Hearts")] * (value - 11)
    return Hand(cards)


def _simple_strategy(hand: Hand) -> str:
    return "stand"


def test_player_initial_wallet() -> None:
    """Player starts with 100 UoM."""
    p = Player(name="Alice", strategy=_simple_strategy)
    assert p.wallet == 100.0


def test_player_bet_fixed_at_1() -> None:
    """Player bet is fixed at 1 UoM."""
    p = Player(name="Alice", strategy=_simple_strategy)
    assert p.bet == 1.0


def test_place_bet_deducts_from_wallet() -> None:
    """place_bet deducts 1 UoM from wallet."""
    p = Player(name="Alice", strategy=_simple_strategy)
    p.place_bet()
    assert p.wallet == 99.0


def test_place_bet_raises_when_insufficient_funds() -> None:
    """place_bet raises ValueError if bet exceeds wallet balance."""
    p = Player(name="Alice", strategy=_simple_strategy)
    p.wallet = 0.0
    with pytest.raises(ValueError, match="wallet"):
        p.place_bet()


def test_receive_payout_adds_to_wallet() -> None:
    """receive_payout adds amount to wallet."""
    p = Player(name="Alice", strategy=_simple_strategy)
    p.receive_payout(1.5)
    assert p.wallet == 101.5


def test_strategy_called_with_hand() -> None:
    """Player.strategy is the callable passed at construction."""
    calls: list[Hand] = []

    def recording_strategy(hand: Hand) -> str:
        calls.append(hand)
        return "stand"

    p = Player(name="Alice", strategy=recording_strategy)
    hand = Hand([Card("7", "Hearts"), Card("9", "Clubs")])
    result = p.strategy(hand)
    assert result == "stand"
    assert calls[0] is hand
