"""Tests for Hand class."""

import pytest

from src.cards import Card
from src.hand import Hand


def card(rank: str, suit: str = "Hearts") -> Card:
    return Card(rank=rank, suit=suit)


class TestHandValue:
    def test_simple_value(self):
        hand = Hand([card("5"), card("7")])
        assert hand.value == 12

    def test_face_cards(self):
        hand = Hand([card("King"), card("Queen")])
        assert hand.value == 20

    def test_ace_as_11(self):
        hand = Hand([card("Ace"), card("9")])
        assert hand.value == 20

    def test_ace_as_1_to_avoid_bust(self):
        hand = Hand([card("Ace"), card("9"), card("5")])
        assert hand.value == 15

    def test_two_aces(self):
        hand = Hand([card("Ace"), card("Ace")])
        assert hand.value == 12

    @pytest.mark.parametrize(
        "ranks,expected",
        [
            (["2", "3", "4", "5", "6"], 20),
            (["10", "King"], 20),
            (["Ace", "King"], 21),
        ],
    )
    def test_parametrized_values(self, ranks, expected):
        hand = Hand([card(r) for r in ranks])
        assert hand.value == expected


class TestHandBlackjack:
    def test_ace_and_king_is_blackjack(self):
        hand = Hand([card("Ace"), card("King")])
        assert hand.is_blackjack is True

    def test_ace_and_10_is_blackjack(self):
        hand = Hand([card("Ace"), card("10")])
        assert hand.is_blackjack is True

    def test_21_with_three_cards_is_not_blackjack(self):
        hand = Hand([card("7"), card("7"), card("7")])
        assert hand.is_blackjack is False

    def test_non_21_is_not_blackjack(self):
        hand = Hand([card("10"), card("9")])
        assert hand.is_blackjack is False


class TestHandBust:
    def test_over_21_is_bust(self):
        hand = Hand([card("King"), card("Queen"), card("5")])
        assert hand.is_bust is True

    def test_exactly_21_is_not_bust(self):
        hand = Hand([card("Ace"), card("King")])
        assert hand.is_bust is False

    def test_under_21_is_not_bust(self):
        hand = Hand([card("10"), card("9")])
        assert hand.is_bust is False
