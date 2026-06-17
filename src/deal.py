"""Deal logic — shuffling and dealing the opening hand."""

from dataclasses import replace

from src.cards import Deck
from src.hand import Hand


def deal_initial(deck: Deck) -> tuple[Hand, Hand]:
    """Deal the opening hand from a shuffled deck.

    Returns (player_hand, dealer_hand). Player receives 2 visible cards.
    Dealer receives 1 visible card and 1 hidden card.
    """
    player_card_1 = deck.deal()
    dealer_card_1 = deck.deal()
    player_card_2 = deck.deal()
    dealer_card_2 = replace(deck.deal(), visible=False)

    player_hand = Hand([player_card_1, player_card_2])
    dealer_hand = Hand([dealer_card_1, dealer_card_2])
    return player_hand, dealer_hand
