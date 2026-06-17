"""Dealer — deterministic hit/stand strategy and hole card reveal."""

from dataclasses import replace

from src.cards import Card
from src.hand import Hand


class Dealer:
    """The blackjack dealer with a fixed hit-on-16-or-under strategy."""

    def strategy(self, hand: Hand) -> str:
        """Return 'hit' if hand value is 16 or under, 'stand' if 17 or above."""
        return "hit" if hand.value <= 16 else "stand"

    def reveal_hole_card(self, hand: Hand) -> Card:
        """Reveal the hidden card in hand. Raises ValueError if no hidden card exists."""
        for i, card in enumerate(hand.cards):
            if not card.visible:
                revealed = replace(card, visible=True)
                hand.cards[i] = revealed
                return revealed
        raise ValueError("No hidden card found in dealer's hand.")
