"""Entry point — play one hand of blackjack with the default strategy."""

from src.game import play_hand
from src.hand import Hand
from src.player import Player


def default_strategy(hand: Hand) -> str:
    """Hit on 16 or under, stand on 17 or above — mirrors dealer strategy."""
    return "hit" if hand.value <= 16 else "stand"


def main() -> None:
    """Create a player and play one hand."""
    player = Player(name="Player", strategy=default_strategy)
    play_hand(player)


if __name__ == "__main__":
    main()
