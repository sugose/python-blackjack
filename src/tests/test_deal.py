"""Tests for deal_initial()."""

from src.cards import Deck
from src.deal import deal_initial
from src.hand import Hand


class TestDealInitial:
    def _shuffled_deck(self, seed: int = 1) -> Deck:
        deck = Deck()
        deck.shuffle(seed=seed)
        return deck

    def test_returns_two_hands(self):
        player_hand, dealer_hand = deal_initial(self._shuffled_deck())
        assert isinstance(player_hand, Hand)
        assert isinstance(dealer_hand, Hand)

    def test_player_hand_has_two_cards(self):
        player_hand, _ = deal_initial(self._shuffled_deck())
        assert len(player_hand.cards) == 2

    def test_dealer_hand_has_two_cards(self):
        _, dealer_hand = deal_initial(self._shuffled_deck())
        assert len(dealer_hand.cards) == 2

    def test_four_cards_removed_from_deck(self):
        deck = self._shuffled_deck()
        deal_initial(deck)
        assert len(deck) == 48

    def test_dealer_has_one_hidden_card(self):
        _, dealer_hand = deal_initial(self._shuffled_deck())
        hidden = [c for c in dealer_hand.cards if not c.visible]
        assert len(hidden) == 1

    def test_player_cards_are_all_visible(self):
        player_hand, _ = deal_initial(self._shuffled_deck())
        assert all(c.visible for c in player_hand.cards)

    def test_dealer_has_one_visible_card(self):
        _, dealer_hand = deal_initial(self._shuffled_deck())
        visible = [c for c in dealer_hand.cards if c.visible]
        assert len(visible) == 1

    def test_no_shared_cards_between_hands(self):
        deck = self._shuffled_deck()
        player_hand, dealer_hand = deal_initial(deck)
        player_ids = {id(c) for c in player_hand.cards}
        dealer_ids = {id(c) for c in dealer_hand.cards}
        assert player_ids.isdisjoint(dealer_ids)
