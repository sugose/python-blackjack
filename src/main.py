"""Entry point — play a session of blackjack with the default strategy."""

import logging

from src.game import play_session
from src.hand import Hand
from src.player import Player


def default_strategy(hand: Hand) -> str:
    """Hit on 16 or under, stand on 17 or above — mirrors dealer strategy."""
    return "hit" if hand.value <= 16 else "stand"


def main() -> None:
    """Create a player and play a session."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    player = Player(name="Player", strategy=default_strategy)
    play_session(player)


if __name__ == "__main__":
    main()
