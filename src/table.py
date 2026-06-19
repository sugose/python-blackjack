"""Table and HouseRules dataclasses for multiplayer blackjack."""

from __future__ import annotations

from dataclasses import dataclass

from src.dealer import Dealer
from src.player import Player

_VALID_NUM_DECKS = {1, 2, 4, 6, 8}


@dataclass
class HouseRules:
    """House rules that govern payout and dealer behaviour."""

    blackjackPayout: float
    dealerHitsOnSoft17: bool


@dataclass
class Table:
    """A blackjack table hosting multiple players sharing a single shoe."""

    tableId: str
    maxSeats: int
    minBet: float
    maxBet: float
    numDecks: int
    players: list[Player]
    dealer: Dealer
    houseRules: HouseRules

    def __post_init__(self) -> None:
        """Validate table configuration at construction time."""
        if self.maxSeats < 1:
            raise ValueError(f"maxSeats must be at least 1, got {self.maxSeats}")
        if len(self.players) > self.maxSeats:
            raise ValueError(
                f"players count ({len(self.players)}) exceeds maxSeats ({self.maxSeats})"
            )
        if self.numDecks not in _VALID_NUM_DECKS:
            raise ValueError(
                f"numDecks must be one of {sorted(_VALID_NUM_DECKS)}, got {self.numDecks}"
            )
        if self.minBet > self.maxBet:
            raise ValueError(f"minBet ({self.minBet}) must not exceed maxBet ({self.maxBet})")
        names = [p.name for p in self.players]
        if len(names) != len(set(names)):
            seen: set[str] = set()
            dupes: set[str] = set()
            for name in names:
                if name in seen:
                    dupes.add(name)
                else:
                    seen.add(name)
            raise ValueError(f"duplicate player names at table: {sorted(dupes)}")
