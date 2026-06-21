"""Human session launcher — python -m src.play"""

import argparse
import sys

from src.dealer import Dealer
from src.player import Player
from src.session import play_table_session
from src.strategy import human_strategy
from src.table import HouseRules, Table

VALID_DECK_COUNTS = {1, 2, 4, 6, 8}


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the human session launcher."""
    parser = argparse.ArgumentParser(description="Play a human blackjack session.")
    parser.add_argument("--name", type=str, default="Player", help="Player name")
    parser.add_argument("--wallet", type=float, default=100.0, help="Starting wallet in UoM")
    parser.add_argument("--bet", type=float, default=1.0, help="Bet per hand in UoM")
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
    """Entry point for the human blackjack session."""
    args = parse_args()

    if args.decks not in VALID_DECK_COUNTS:
        print(
            f"Error: --decks must be one of {sorted(VALID_DECK_COUNTS)}, got {args.decks}",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.hands < 1:
        print(f"Error: --hands must be at least 1, got {args.hands}", file=sys.stderr)
        sys.exit(1)

    if args.bet <= 0:
        print(f"Error: --bet must be greater than 0, got {args.bet}", file=sys.stderr)
        sys.exit(1)

    player = Player(name=args.name, strategy=human_strategy, wallet=args.wallet)
    player.bet = args.bet

    house_rules = HouseRules(blackjackPayout=1.5, dealerHitsOnSoft17=True)
    dealer = Dealer()
    table = Table(
        tableId="table-1",
        maxSeats=7,
        minBet=args.bet,
        maxBet=args.bet * 100,
        numDecks=args.decks,
        players=[player],
        dealer=dealer,
        houseRules=house_rules,
    )

    play_table_session(table, seed=args.seed, max_hands=args.hands)


if __name__ == "__main__":
    main()
