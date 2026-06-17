"""Tests for Card and Deck classes."""

import pytest

from src.cards import Card, Deck


class TestCard:
    def test_numeric_card_value(self):
        for rank in range(2, 11):
            card = Card(rank=str(rank), suit="Hearts")
            assert card.value == rank

    def test_face_card_value(self):
        for rank in ("Jack", "Queen", "King"):
            card = Card(rank=rank, suit="Spades")
            assert card.value == 10

    def test_ace_value(self):
        card = Card(rank="Ace", suit="Diamonds")
        assert card.value == 11

    def test_card_immutability(self):
        card = Card(rank="5", suit="Clubs")
        with pytest.raises((AttributeError, TypeError)):
            card.rank = "6"  # type: ignore[misc]

    def test_card_repr(self):
        card = Card(rank="Ace", suit="Spades")
        assert "Ace" in repr(card)
        assert "Spades" in repr(card)


class TestDeck:
    def test_deck_has_52_cards(self):
        deck = Deck()
        assert len(deck) == 52

    def test_deck_has_all_suits_and_ranks(self):
        deck = Deck()
        cards = [deck.deal() for _ in range(52)]
        suits = {c.suit for c in cards}
        ranks = {c.rank for c in cards}
        assert suits == {"Hearts", "Diamonds", "Clubs", "Spades"}
        assert ranks == {
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
            "Ace",
        }

    def test_deck_has_no_duplicates(self):
        deck = Deck()
        cards = [deck.deal() for _ in range(52)]
        pairs = [(c.rank, c.suit) for c in cards]
        assert len(pairs) == len(set(pairs))

    def test_shuffle_with_seed_is_reproducible(self):
        deck1 = Deck()
        deck1.shuffle(seed=42)
        order1 = [(deck1.deal().rank, deck1.deal().suit) for _ in range(5)]

        deck2 = Deck()
        deck2.shuffle(seed=42)
        order2 = [(deck2.deal().rank, deck2.deal().suit) for _ in range(5)]

        assert order1 == order2

    def test_deal_removes_card_from_deck(self):
        deck = Deck()
        deck.deal()
        assert len(deck) == 51

    def test_deal_from_empty_deck_raises(self):
        deck = Deck()
        for _ in range(52):
            deck.deal()
        with pytest.raises(Exception, match="[Ee]mpty"):
            deck.deal()
