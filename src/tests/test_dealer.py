"""Tests for src/dealer.py."""

import pytest

from src.cards import Card
from src.dealer import Dealer
from src.hand import Hand


def test_dealer_strategy_hits_on_16() -> None:
    """Dealer strategy returns 'hit' when hand value is 16."""
    d = Dealer()
    hand = Hand([Card("9", "Hearts"), Card("7", "Clubs")])
    assert hand.value == 16
    assert d.strategy(hand) == "hit"


def test_dealer_strategy_stands_on_17() -> None:
    """Dealer strategy returns 'stand' when hand value is 17."""
    d = Dealer()
    hand = Hand([Card("9", "Hearts"), Card("8", "Clubs")])
    assert hand.value == 17
    assert d.strategy(hand) == "stand"


def test_dealer_strategy_stands_above_17() -> None:
    """Dealer strategy returns 'stand' when hand value is above 17."""
    d = Dealer()
    hand = Hand([Card("10", "Hearts"), Card("9", "Clubs")])
    assert hand.value == 19
    assert d.strategy(hand) == "stand"


def test_dealer_strategy_hits_on_soft_16() -> None:
    """Dealer strategy hits on hand value under 17 even with Ace."""
    d = Dealer()
    hand = Hand([Card("Ace", "Hearts"), Card("5", "Clubs")])
    assert hand.value == 16
    assert d.strategy(hand) == "hit"


def test_reveal_hole_card_returns_card() -> None:
    """reveal_hole_card returns the hidden card from the dealer's hand."""
    d = Dealer()
    from dataclasses import replace

    hidden = replace(Card("King", "Hearts"), visible=False)
    hand = Hand([Card("7", "Diamonds"), hidden])
    revealed = d.reveal_hole_card(hand)
    assert revealed.rank == "King"
    assert revealed.suit == "Hearts"


def test_reveal_hole_card_makes_card_visible() -> None:
    """reveal_hole_card makes the hidden card visible in the hand."""
    d = Dealer()
    from dataclasses import replace

    hidden = replace(Card("King", "Hearts"), visible=False)
    hand = Hand([Card("7", "Diamonds"), hidden])
    d.reveal_hole_card(hand)
    assert all(c.visible for c in hand.cards)


def test_reveal_hole_card_raises_if_no_hidden_card() -> None:
    """reveal_hole_card raises ValueError if no hidden card exists."""
    d = Dealer()
    hand = Hand([Card("7", "Diamonds"), Card("King", "Hearts")])
    with pytest.raises(ValueError, match="hidden"):
        d.reveal_hole_card(hand)
