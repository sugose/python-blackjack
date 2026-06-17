"""Hand — a collection of cards with a calculated value."""

from src.cards import Card


class Hand:
    """A player's or dealer's hand of cards."""

    def __init__(self, cards: list[Card]) -> None:
        self.cards: list[Card] = list(cards)

    @property
    def value(self) -> int:
        """Total hand value, counting Aces as 11 then reducing to 1 to avoid bust."""
        total = sum(c.value for c in self.cards)
        aces = sum(1 for c in self.cards if c.rank == "Ace")
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    @property
    def is_blackjack(self) -> bool:
        """True if the hand is exactly 21 with exactly 2 cards."""
        return len(self.cards) == 2 and self.value == 21

    @property
    def is_bust(self) -> bool:
        """True if the hand value exceeds 21."""
        return self.value > 21

    def __repr__(self) -> str:
        return f"Hand({self.cards!r}, value={self.value})"
