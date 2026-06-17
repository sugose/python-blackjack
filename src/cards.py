"""Card and Deck — the building blocks of the game."""

import random
from dataclasses import dataclass

RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace")
SUITS = ("Hearts", "Diamonds", "Clubs", "Spades")

_FACE_VALUE: dict[str, int] = {
    **{str(n): n for n in range(2, 11)},
    "Jack": 10,
    "Queen": 10,
    "King": 10,
    "Ace": 11,
}


@dataclass(frozen=True)
class Card:
    """A single playing card with a rank, suit, visibility flag, and numeric value."""

    rank: str
    suit: str
    visible: bool = True

    def __post_init__(self) -> None:
        """Validate rank and suit at construction time."""
        if self.rank not in _FACE_VALUE:
            raise ValueError(f"Invalid card rank: {self.rank!r}")
        if self.suit not in SUITS:
            raise ValueError(f"Invalid card suit: {self.suit!r}")

    @property
    def value(self) -> int:
        """Numeric value of the card (Ace = 11 by default; Hand handles the 1/11 choice)."""
        return _FACE_VALUE[self.rank]

    def __repr__(self) -> str:
        hidden = "" if self.visible else " [hidden]"
        return f"{self.rank} of {self.suit}{hidden}"


class Deck:
    """A standard 52-card deck that can be shuffled and dealt from."""

    def __init__(self) -> None:
        self._cards: list[Card] = [
            Card(rank=r, suit=s) for s in reversed(SUITS) for r in reversed(RANKS)
        ]

    def __len__(self) -> int:
        return len(self._cards)

    def shuffle(self, seed: int | None = None) -> None:
        """Shuffle the deck in place. Pass a seed for reproducible results."""
        rng = random.Random(seed)
        rng.shuffle(self._cards)

    def deal(self) -> Card:
        """Remove and return the top card from the deck."""
        if not self._cards:
            raise ValueError("Cannot deal from an empty deck.")
        return self._cards.pop()
