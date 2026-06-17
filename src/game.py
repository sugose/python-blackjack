"""Game engine — orchestrates a single blackjack hand or a full session."""

from src.cards import Deck
from src.deal import deal_initial
from src.dealer import Dealer
from src.logger import log_event
from src.player import Player


def _log_wallet(player: Player) -> None:
    """Log wallet balance and player departure if wallet reaches zero."""
    log_event("WALLET", f"Player wallet: {player.wallet:g} UoM")
    if player.wallet == 0.0:
        log_event("LEAVE", "Player leaves — wallet reached 0 UoM")


def play_hand(player: Player, deck: Deck) -> None:
    """Play one complete hand of blackjack for the given player using the provided deck."""
    dealer = Dealer()

    player.place_bet()
    log_event("BET", f"Player bets {player.bet:g} UoM — wallet: {player.wallet:g} UoM")

    player_hand, dealer_hand = deal_initial(deck)

    c1 = player_hand.cards[0]
    c2 = player_hand.cards[1]
    log_event("DEAL", f"Player dealt {c1} — card value: {c1.value}")
    log_event("DEAL", f"Player dealt {c2} — hand value: {player_hand.value}")
    dc1 = dealer_hand.cards[0]
    log_event("DEAL", f"Dealer shows {dc1} — card value: {dc1.value}")
    log_event("DEAL", "Dealer has 1 hidden card")

    if player_hand.is_blackjack:
        if dealer_hand.is_blackjack:
            revealed = dealer.reveal_hole_card(dealer_hand)
            log_event("REVEAL", f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}")
            log_event("OUTCOME", "Push — both have blackjack")
            player.receive_payout(player.bet)
            log_event("PAYOUT", f"Player receives {player.bet:g} UoM — push")
        else:
            log_event("OUTCOME", "Player blackjack — pays 3:2")
            payout = player.bet + player.bet * 1.5
            player.receive_payout(payout)
            log_event("PAYOUT", f"Player receives {payout:g} UoM — blackjack 3:2")
        _log_wallet(player)
        return

    if dealer_hand.is_blackjack:
        revealed = dealer.reveal_hole_card(dealer_hand)
        log_event("REVEAL", f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}")
        log_event("OUTCOME", "Dealer blackjack — player loses")
        _log_wallet(player)
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
        _log_wallet(player)
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
        payout = player.bet * 2
        player.receive_payout(payout)
        log_event("PAYOUT", f"Player receives {payout:g} UoM — win")
        _log_wallet(player)
        return

    pv = player_hand.value
    dv = dealer_hand.value

    if pv > dv:
        log_event("OUTCOME", f"Player wins — player {pv} beats dealer {dv}")
        payout = player.bet * 2
        player.receive_payout(payout)
        log_event("PAYOUT", f"Player receives {payout:g} UoM — win")
    elif dv > pv:
        log_event("OUTCOME", f"Dealer wins — dealer {dv} beats player {pv}")
    else:
        log_event("OUTCOME", f"Push — both have {pv}")
        player.receive_payout(player.bet)
        log_event("PAYOUT", f"Player receives {player.bet:g} UoM — push")

    _log_wallet(player)


def play_session(
    player: Player,
    max_hands: int = 10,
    cut_card: int = 39,
    seed: int | None = None,
) -> None:
    """Play a session of multiple blackjack hands for the given player."""
    if max_hands < 1:
        raise ValueError(f"max_hands must be at least 1, got {max_hands}")
    if cut_card < 1 or cut_card >= 52:
        raise ValueError(f"cut_card must be between 1 and 51, got {cut_card}")

    log_event(
        "OPEN",
        f"Session started — player: {player.name}, max hands: {max_hands}, "
        f"starting wallet: {player.wallet:g} UoM",
    )

    deck = Deck()
    deck.shuffle(seed=seed)
    log_event("SHUFFLE", f"Shuffled {len(deck)}-card deck")

    for hand_number in range(1, max_hands + 1):
        log_event("HAND", f"Hand {hand_number} of {max_hands} — wallet: {player.wallet:g} UoM")
        play_hand(player, deck)

        if player.wallet == 0.0:
            log_event("LEAVE", "Player leaves — no funds")
            log_event(
                "CLOSE",
                f"Session closed — hands played: {hand_number}, final wallet: 0 UoM, "
                "reason: no funds",
            )
            return

        if len(deck) <= cut_card:
            log_event("CUT", "Cut card reached — reshuffling after this hand")
            deck = Deck()
            deck.shuffle(seed=seed + hand_number if seed is not None else None)
            log_event("SHUFFLE", f"Shuffled {len(deck)}-card deck")

    log_event("LEAVE", "Player leaves — max hands reached")
    log_event(
        "CLOSE",
        f"Session closed — hands played: {max_hands}, final wallet: {player.wallet:g} UoM, "
        "reason: max hands reached",
    )
