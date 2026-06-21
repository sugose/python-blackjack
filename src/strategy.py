"""Player strategy utilities — adapt() and built-in strategies."""

import inspect
from typing import Callable

from src.cards import Card
from src.hand import Hand

# Canonical two-argument strategy type: hand + dealer upcard → action
Strategy = Callable[[Hand, Card], str]


def adapt(strategy: Callable) -> Strategy:
    """Wrap a one-argument strategy (Hand only) to accept the two-argument signature.

    Allows existing Callable[[Hand], str] strategies to work unchanged alongside
    the new Callable[[Hand, Card], str] interface.
    """
    try:
        sig = inspect.signature(strategy)
        n = len([p for p in sig.parameters.values() if p.default is inspect.Parameter.empty])
    except (ValueError, TypeError):
        n = 1  # conservative fallback — assume one required arg

    if n >= 2:
        return strategy  # already two-argument
    return lambda hand, upcard: strategy(hand)


def human_strategy(hand: Hand, upcard: Card) -> str:
    """Interactive CLI strategy — prompts the human for hit or stand.

    Displays the player's current hand value and the dealer's visible upcard
    before each decision. Loops until a valid response is received.
    """
    print(f"\n  Your hand : {', '.join(str(c) for c in hand.cards)} (value: {hand.value})")
    print(f"  Dealer shows: {upcard}")
    while True:
        choice = input("  Hit or stand? [h/s]: ").strip().lower()
        if choice in ("h", "hit"):
            return "hit"
        if choice in ("s", "stand"):
            return "stand"
        print("  Please enter 'h' for hit or 's' for stand.")
