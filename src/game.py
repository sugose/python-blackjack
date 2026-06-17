"""Game engine — orchestrates a single blackjack hand end-to-end."""

from src.cards import Deck
from src.deal import deal_initial
from src.dealer import Dealer
from src.hand import Hand
from src.logger import log_event
from src.player import Player


def play_hand(player: Player, seed: int | None = None) -> None:
    """Play one complete hand of blackjack for the given player."""
    dealer = Dealer()

    player.place_bet()
    log_event("BET", f"Player bets {player.bet:.0f} UoM — wallet: {player.wallet:.0f} UoM")

    deck = Deck()
    deck.shuffle(seed=seed)
    log_event("DECK", f"Shuffled {len(deck)}-card deck")

    player_hand, dealer_hand = deal_initial(deck)

    c1 = player_hand.cards[0]
    c2 = player_hand.cards[1]
    log_event("DEAL", f"Player dealt {c1} — hand value: {Hand([c1]).value}")
    log_event("DEAL", f"Player dealt {c2} — hand value: {player_hand.value}")
    dc1 = dealer_hand.cards[0]
    log_event("DEAL", f"Dealer shows {dc1} — hand value: {Hand([dc1]).value}")
    log_event("DEAL", "Dealer has 1 hidden card")

    if player_hand.is_blackjack:
        if dealer_hand.is_blackjack:
            revealed = dealer.reveal_hole_card(dealer_hand)
            log_event("REVEAL", f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}")
            log_event("OUTCOME", "Push — both have blackjack")
            player.receive_payout(player.bet)
        else:
            log_event("OUTCOME", "Player blackjack — pays 3:2")
            player.receive_payout(player.bet + player.bet * 1.5)
        log_event("WALLET", f"Player wallet: {player.wallet:.0f} UoM")
        if player.wallet == 0.0:
            log_event("TABLE", "Player leaves — wallet reached 0 UoM")
        return

    while not player_hand.is_bust:
        action = player.strategy(player_hand)
        if action not in ("hit", "stand"):
            raise ValueError(f"Unknown strategy action: {action!r}. Must be 'hit' or 'stand'.")
        if action == "stand":
            log_event("STAND", f"Player stands on {player_hand.value}")
            break
        card = deck.deal()
        player_hand.cards.append(card)
        log_event("HIT", f"Player hits: {card} — hand value: {player_hand.value}")

    if player_hand.is_bust:
        log_event("BUST", f"Player busts with {player_hand.value}")
        log_event("WALLET", f"Player wallet: {player.wallet:.0f} UoM")
        if player.wallet == 0.0:
            log_event("TABLE", "Player leaves — wallet reached 0 UoM")
        return

    revealed = dealer.reveal_hole_card(dealer_hand)
    log_event("REVEAL", f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}")

    while not dealer_hand.is_bust:
        action = dealer.strategy(dealer_hand)
        if action == "stand":
            log_event("STAND", f"Dealer stands on {dealer_hand.value}")
            break
        card = deck.deal()
        dealer_hand.cards.append(card)
        log_event("HIT", f"Dealer hits: {card} — hand value: {dealer_hand.value}")

    if dealer_hand.is_bust:
        log_event("BUST", f"Dealer busts with {dealer_hand.value}")
        log_event("OUTCOME", "Player wins — dealer busts")
        player.receive_payout(player.bet * 2)
        log_event("WALLET", f"Player wallet: {player.wallet:.0f} UoM")
        if player.wallet == 0.0:
            log_event("TABLE", "Player leaves — wallet reached 0 UoM")
        return

    pv = player_hand.value
    dv = dealer_hand.value

    if pv > dv:
        log_event("OUTCOME", f"Player wins — player {pv} beats dealer {dv}")
        player.receive_payout(player.bet * 2)
    elif dv > pv:
        log_event("OUTCOME", f"Dealer wins — dealer {dv} beats player {pv}")
    else:
        log_event("OUTCOME", f"Push — both have {pv}")
        player.receive_payout(player.bet)

    log_event("WALLET", f"Player wallet: {player.wallet:.0f} UoM")
    if player.wallet == 0.0:
        log_event("TABLE", "Player leaves — wallet reached 0 UoM")
