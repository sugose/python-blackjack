"""Game engine — orchestrates a single blackjack hand or a full session."""

from pathlib import Path
from uuid import uuid4

from src.cards import Deck
from src.deal import deal_initial
from src.dealer import Dealer
from src.logger import GameEvent, emit_event
from src.player import Player


def _emit_wallet(player: Player, session_id: str, hand_id: str, session_file: Path) -> None:
    """Emit WALLET event and LEAVE event if wallet reaches zero."""
    emit_event(
        GameEvent(
            eventType="WALLET",
            sessionId=session_id,
            handId=hand_id,
            actor=player.name,
            data={
                "wallet": player.wallet,
                "message": f"Player wallet: {player.wallet:g} UoM",
            },
        ),
        session_file,
    )
    if player.wallet == 0.0:
        emit_event(
            GameEvent(
                eventType="LEAVE",
                sessionId=session_id,
                actor=player.name,
                data={
                    "reason": "no funds",
                    "message": "Player leaves — wallet reached 0 UoM",
                },
            ),
            session_file,
        )


def play_hand(player: Player, session_id: str, session_file: Path, deck: Deck) -> None:
    """Play one complete hand of blackjack for the given player using the provided deck."""
    hand_id = str(uuid4())
    dealer = Dealer()

    player.place_bet()
    emit_event(
        GameEvent(
            eventType="BET",
            sessionId=session_id,
            handId=hand_id,
            actor=player.name,
            data={
                "bet": player.bet,
                "wallet": player.wallet,
                "message": f"Player bets {player.bet:g} UoM — wallet: {player.wallet:g} UoM",
            },
        ),
        session_file,
    )

    player_hand, dealer_hand = deal_initial(deck)

    c1 = player_hand.cards[0]
    c2 = player_hand.cards[1]
    emit_event(
        GameEvent(
            eventType="DEAL",
            sessionId=session_id,
            handId=hand_id,
            actor=player.name,
            data={
                "card": str(c1),
                "cardValue": c1.value,
                "message": f"Player dealt {c1} — card value: {c1.value}",
            },
        ),
        session_file,
    )
    emit_event(
        GameEvent(
            eventType="DEAL",
            sessionId=session_id,
            handId=hand_id,
            actor=player.name,
            data={
                "card": str(c2),
                "handValue": player_hand.value,
                "message": f"Player dealt {c2} — hand value: {player_hand.value}",
            },
        ),
        session_file,
    )
    dc1 = dealer_hand.cards[0]
    emit_event(
        GameEvent(
            eventType="DEAL",
            sessionId=session_id,
            handId=hand_id,
            actor="Dealer",
            data={
                "card": str(dc1),
                "cardValue": dc1.value,
                "message": f"Dealer shows {dc1} — card value: {dc1.value}",
            },
        ),
        session_file,
    )
    emit_event(
        GameEvent(
            eventType="DEAL",
            sessionId=session_id,
            handId=hand_id,
            actor="Dealer",
            data={"message": "Dealer has 1 hidden card"},
        ),
        session_file,
    )

    if player_hand.is_blackjack:
        if dealer_hand.is_blackjack:
            revealed = dealer.reveal_hole_card(dealer_hand)
            emit_event(
                GameEvent(
                    eventType="REVEAL",
                    sessionId=session_id,
                    handId=hand_id,
                    actor="Dealer",
                    data={
                        "card": str(revealed),
                        "handValue": dealer_hand.value,
                        "message": f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}",
                    },
                ),
                session_file,
            )
            emit_event(
                GameEvent(
                    eventType="OUTCOME",
                    sessionId=session_id,
                    handId=hand_id,
                    data={"result": "push", "message": "Push — both have blackjack"},
                ),
                session_file,
            )
            player.receive_payout(player.bet)
            emit_event(
                GameEvent(
                    eventType="PAYOUT",
                    sessionId=session_id,
                    handId=hand_id,
                    actor=player.name,
                    data={
                        "amount": player.bet,
                        "reason": "push",
                        "message": f"Player receives {player.bet:g} UoM — push",
                    },
                ),
                session_file,
            )
        else:
            emit_event(
                GameEvent(
                    eventType="OUTCOME",
                    sessionId=session_id,
                    handId=hand_id,
                    data={
                        "result": "player_blackjack",
                        "message": "Player blackjack — pays 3:2",
                    },
                ),
                session_file,
            )
            payout = player.bet + player.bet * 1.5
            player.receive_payout(payout)
            emit_event(
                GameEvent(
                    eventType="PAYOUT",
                    sessionId=session_id,
                    handId=hand_id,
                    actor=player.name,
                    data={
                        "amount": payout,
                        "reason": "blackjack 3:2",
                        "message": f"Player receives {payout:g} UoM — blackjack 3:2",
                    },
                ),
                session_file,
            )
        _emit_wallet(player, session_id, hand_id, session_file)
        return

    if dealer_hand.is_blackjack:
        revealed = dealer.reveal_hole_card(dealer_hand)
        emit_event(
            GameEvent(
                eventType="REVEAL",
                sessionId=session_id,
                handId=hand_id,
                actor="Dealer",
                data={
                    "card": str(revealed),
                    "handValue": dealer_hand.value,
                    "message": f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}",
                },
            ),
            session_file,
        )
        emit_event(
            GameEvent(
                eventType="OUTCOME",
                sessionId=session_id,
                handId=hand_id,
                data={
                    "result": "dealer_blackjack",
                    "message": "Dealer blackjack — player loses",
                },
            ),
            session_file,
        )
        _emit_wallet(player, session_id, hand_id, session_file)
        return

    while not player_hand.is_bust:
        action = player.strategy(player_hand)
        if action not in ("hit", "stand"):
            raise ValueError(f"Unknown strategy action: {action!r}. Must be 'hit' or 'stand'.")
        if action == "stand":
            emit_event(
                GameEvent(
                    eventType="STAND",
                    sessionId=session_id,
                    handId=hand_id,
                    actor=player.name,
                    data={
                        "handValue": player_hand.value,
                        "message": f"Player stands on {player_hand.value}",
                    },
                ),
                session_file,
            )
            break
        card = deck.deal()
        player_hand.cards.append(card)
        emit_event(
            GameEvent(
                eventType="HIT",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "card": str(card),
                    "handValue": player_hand.value,
                    "message": f"Player hits: {card} — hand value: {player_hand.value}",
                },
            ),
            session_file,
        )

    if player_hand.is_bust:
        emit_event(
            GameEvent(
                eventType="BUST",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "handValue": player_hand.value,
                    "message": f"Player busts with {player_hand.value}",
                },
            ),
            session_file,
        )
        _emit_wallet(player, session_id, hand_id, session_file)
        return

    revealed = dealer.reveal_hole_card(dealer_hand)
    emit_event(
        GameEvent(
            eventType="REVEAL",
            sessionId=session_id,
            handId=hand_id,
            actor="Dealer",
            data={
                "card": str(revealed),
                "handValue": dealer_hand.value,
                "message": f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}",
            },
        ),
        session_file,
    )

    while not dealer_hand.is_bust:
        action = dealer.strategy(dealer_hand)
        if action == "stand":
            emit_event(
                GameEvent(
                    eventType="STAND",
                    sessionId=session_id,
                    handId=hand_id,
                    actor="Dealer",
                    data={
                        "handValue": dealer_hand.value,
                        "message": f"Dealer stands on {dealer_hand.value}",
                    },
                ),
                session_file,
            )
            break
        card = deck.deal()
        dealer_hand.cards.append(card)
        emit_event(
            GameEvent(
                eventType="HIT",
                sessionId=session_id,
                handId=hand_id,
                actor="Dealer",
                data={
                    "card": str(card),
                    "handValue": dealer_hand.value,
                    "message": f"Dealer hits: {card} — hand value: {dealer_hand.value}",
                },
            ),
            session_file,
        )

    if dealer_hand.is_bust:
        emit_event(
            GameEvent(
                eventType="BUST",
                sessionId=session_id,
                handId=hand_id,
                actor="Dealer",
                data={
                    "handValue": dealer_hand.value,
                    "message": f"Dealer busts with {dealer_hand.value}",
                },
            ),
            session_file,
        )
        emit_event(
            GameEvent(
                eventType="OUTCOME",
                sessionId=session_id,
                handId=hand_id,
                data={"result": "player_wins", "message": "Player wins — dealer busts"},
            ),
            session_file,
        )
        payout = player.bet * 2
        player.receive_payout(payout)
        emit_event(
            GameEvent(
                eventType="PAYOUT",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "amount": payout,
                    "reason": "win",
                    "message": f"Player receives {payout:g} UoM — win",
                },
            ),
            session_file,
        )
        _emit_wallet(player, session_id, hand_id, session_file)
        return

    pv = player_hand.value
    dv = dealer_hand.value

    if pv > dv:
        emit_event(
            GameEvent(
                eventType="OUTCOME",
                sessionId=session_id,
                handId=hand_id,
                data={
                    "result": "player_wins",
                    "message": f"Player wins — player {pv} beats dealer {dv}",
                },
            ),
            session_file,
        )
        payout = player.bet * 2
        player.receive_payout(payout)
        emit_event(
            GameEvent(
                eventType="PAYOUT",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "amount": payout,
                    "reason": "win",
                    "message": f"Player receives {payout:g} UoM — win",
                },
            ),
            session_file,
        )
    elif dv > pv:
        emit_event(
            GameEvent(
                eventType="OUTCOME",
                sessionId=session_id,
                handId=hand_id,
                data={
                    "result": "dealer_wins",
                    "message": f"Dealer wins — dealer {dv} beats player {pv}",
                },
            ),
            session_file,
        )
    else:
        emit_event(
            GameEvent(
                eventType="OUTCOME",
                sessionId=session_id,
                handId=hand_id,
                data={"result": "push", "message": f"Push — both have {pv}"},
            ),
            session_file,
        )
        player.receive_payout(player.bet)
        emit_event(
            GameEvent(
                eventType="PAYOUT",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "amount": player.bet,
                    "reason": "push",
                    "message": f"Player receives {player.bet:g} UoM — push",
                },
            ),
            session_file,
        )

    _emit_wallet(player, session_id, hand_id, session_file)


def play_hand_standalone(player: Player, seed: int | None = None) -> None:
    """Temporary wrapper — plays one hand with its own session context."""
    session_id = str(uuid4())
    session_file = Path(f"logs/session-{session_id[-8:]}.jsonl")
    deck = Deck()
    deck.shuffle(seed=seed)
    play_hand(player, session_id, session_file, deck)


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

    session_id = str(uuid4())
    session_file = Path(f"logs/session-{session_id[-8:]}.jsonl")

    emit_event(
        GameEvent(
            eventType="OPEN",
            sessionId=session_id,
            data={
                "player": player.name,
                "maxHands": max_hands,
                "startingWallet": player.wallet,
                "message": (
                    f"Session started — player: {player.name}, max hands: {max_hands}, "
                    f"starting wallet: {player.wallet:g} UoM"
                ),
            },
        ),
        session_file,
    )

    deck = Deck()
    deck.shuffle(seed=seed)
    emit_event(
        GameEvent(
            eventType="SHUFFLE",
            sessionId=session_id,
            data={"deckSize": len(deck), "message": f"Shuffled {len(deck)}-card deck"},
        ),
        session_file,
    )

    for hand_number in range(1, max_hands + 1):
        emit_event(
            GameEvent(
                eventType="HAND",
                sessionId=session_id,
                data={
                    "handNumber": hand_number,
                    "maxHands": max_hands,
                    "wallet": player.wallet,
                    "message": (
                        f"Hand {hand_number} of {max_hands} — wallet: {player.wallet:g} UoM"
                    ),
                },
            ),
            session_file,
        )
        play_hand(player, session_id, session_file, deck)

        if player.wallet == 0.0:
            emit_event(
                GameEvent(
                    eventType="LEAVE",
                    sessionId=session_id,
                    actor=player.name,
                    data={"reason": "no funds", "message": "Player leaves — no funds"},
                ),
                session_file,
            )
            emit_event(
                GameEvent(
                    eventType="CLOSE",
                    sessionId=session_id,
                    data={
                        "handsPlayed": hand_number,
                        "finalWallet": 0,
                        "reason": "no funds",
                        "message": (
                            f"Session closed — hands played: {hand_number}, "
                            "final wallet: 0 UoM, reason: no funds"
                        ),
                    },
                ),
                session_file,
            )
            return

        if len(deck) <= cut_card:
            emit_event(
                GameEvent(
                    eventType="CUT",
                    sessionId=session_id,
                    data={"message": "Cut card reached — reshuffling after this hand"},
                ),
                session_file,
            )
            deck = Deck()
            deck.shuffle(seed=seed + hand_number if seed is not None else None)
            emit_event(
                GameEvent(
                    eventType="SHUFFLE",
                    sessionId=session_id,
                    data={"deckSize": len(deck), "message": f"Shuffled {len(deck)}-card deck"},
                ),
                session_file,
            )

    emit_event(
        GameEvent(
            eventType="LEAVE",
            sessionId=session_id,
            actor=player.name,
            data={
                "reason": "max hands reached",
                "message": "Player leaves — max hands reached",
            },
        ),
        session_file,
    )
    emit_event(
        GameEvent(
            eventType="CLOSE",
            sessionId=session_id,
            data={
                "handsPlayed": max_hands,
                "finalWallet": player.wallet,
                "reason": "max hands reached",
                "message": (
                    f"Session closed — hands played: {max_hands}, "
                    f"final wallet: {player.wallet:g} UoM, reason: max hands reached"
                ),
            },
        ),
        session_file,
    )
