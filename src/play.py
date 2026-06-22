"""Mixed-player table launcher — python -m src.play"""

import argparse
import sys
from typing import Callable

from src.dealer import Dealer
from src.player import Player
from src.session import play_table_session
from src.strategy import human_strategy
from src.table import HouseRules, Table

VALID_DECK_COUNTS = {1, 2, 4, 6, 8}

_STRATEGIES: dict[str, Callable] = {
    "human": human_strategy,
    "mirror": lambda hand, upcard: "hit" if hand.value <= 16 else "stand",
    "hit": lambda hand, upcard: "hit",
    "stand": lambda hand, upcard: "stand",
}


def _error(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def _parse_player_spec(spec: str) -> Player:
    """Parse a 'name:strategy:wallet' spec into a Player. Calls _error on bad input."""
    parts = spec.split(":")
    if len(parts) != 3:
        _error(f"invalid player spec '{spec}' — expected name:strategy:wallet")
    name, strategy_name, wallet_str = parts
    if strategy_name not in _STRATEGIES:
        _error(f"unknown strategy '{strategy_name}' in spec '{spec}'")
    try:
        wallet = float(wallet_str)
    except ValueError:
        _error(f"invalid wallet '{wallet_str}' in spec '{spec}' — must be a number")
    if wallet <= 0:
        _error(f"wallet must be > 0 in spec '{spec}', got {wallet}")
    return Player(name=name, strategy=_STRATEGIES[strategy_name], wallet=wallet)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the mixed-player table launcher."""
    parser = argparse.ArgumentParser(description="Play a blackjack session with mixed players.")
    parser.add_argument(
        "--players",
        nargs="+",
        metavar="SPEC",
        help="One or more player specs: name:strategy:wallet",
    )
    parser.add_argument(
        "--decks",
        type=int,
        default=6,
        help="Number of decks in shoe. Must be one of {1, 2, 4, 6, 8}",
    )
    parser.add_argument("--hands", type=int, default=10, help="Maximum number of hands to play")
    parser.add_argument("--seed", type=int, default=None, help="Optional random seed")
    return parser.parse_args()


def main() -> None:
    """Entry point for the mixed-player blackjack session."""
    args = parse_args()

    if not args.players:
        _error("--players is required — provide at least one name:strategy:wallet spec")

    players = [_parse_player_spec(spec) for spec in args.players]

    names = [p.name for p in players]
    seen: set[str] = set()
    for name in names:
        if name in seen:
            _error(f"duplicate player name '{name}'")
        seen.add(name)

    if args.decks not in VALID_DECK_COUNTS:
        _error(f"--decks must be one of {sorted(VALID_DECK_COUNTS)}, got {args.decks}")

    if args.hands < 1:
        _error(f"--hands must be at least 1, got {args.hands}")

    house_rules = HouseRules(blackjackPayout=1.5, dealerHitsOnSoft17=True)
    table = Table(
        tableId="table-1",
        maxSeats=len(players),
        minBet=1.0,
        maxBet=100.0,
        numDecks=args.decks,
        players=players,
        dealer=Dealer(),
        houseRules=house_rules,
    )

    play_table_session(table, seed=args.seed, max_hands=args.hands)


if __name__ == "__main__":
    main()
