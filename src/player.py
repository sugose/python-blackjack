"""Player — wallet, bet, and pluggable hit/stand strategy."""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Player:
    """A blackjack player with a wallet and a pluggable strategy."""

    name: str
    strategy: Callable
    wallet: float = field(default=100.0)
    vip: bool = field(default=False)
    bet: float = field(default=1.0, init=False)

    def place_bet(self) -> None:
        """Deduct the fixed bet from the wallet. Raises ValueError if funds are insufficient."""
        if self.bet > self.wallet:
            raise ValueError(
                f"Cannot place bet of {self.bet} UoM — wallet has only {self.wallet} UoM."
            )
        self.wallet -= self.bet

    def receive_payout(self, amount: float) -> None:
        """Add amount to the wallet."""
        self.wallet += amount
