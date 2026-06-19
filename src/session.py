"""Multiplayer session loop — play_table_session()."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.cards import Card, Deck
from src.hand import Hand
from src.logger import GameEvent, emit_event
from src.player import Player
from src.table import Table


def _is_soft_17(hand: Hand) -> bool:
    """Return True if the hand is a soft 17 (Ace counted as 11, total == 17)."""
    raw = sum(c.value for c in hand.cards)
    reductions = (raw - hand.value) // 10
    aces = sum(1 for c in hand.cards if c.rank == "Ace")
    return hand.value == 17 and (aces - reductions) > 0


def _build_shoe(num_decks: int, seed: int | None) -> Deck:
    """Build and shuffle a shoe of num_decks standard decks."""
    shoe = Deck()
    # Extend with additional decks beyond the first
    for _ in range(num_decks - 1):
        extra = Deck()
        shoe._cards.extend(extra._cards)  # noqa: SLF001
    shoe.shuffle(seed=seed)
    return shoe


def _emit(event: GameEvent, session_file: Path) -> None:
    emit_event(event, session_file)


def _deal_player_hand(shoe: Deck) -> Hand:
    """Deal 2 visible cards to a player."""
    return Hand([shoe.deal(), shoe.deal()])


def _deal_dealer_hand(shoe: Deck) -> Hand:
    """Deal 1 visible + 1 hidden card to the dealer."""
    visible = shoe.deal()
    hidden = replace(shoe.deal(), visible=False)
    return Hand([visible, hidden])


def _emit_card_dealt(
    card: Card,
    actor: str,
    hand_value: int | None,
    session_id: str,
    hand_id: str,
    session_file: Path,
    *,
    is_hidden: bool = False,
) -> None:
    if is_hidden:
        _emit(
            GameEvent(
                eventType="CardDealt",
                sessionId=session_id,
                handId=hand_id,
                actor=actor,
                data={"message": "Dealer has 1 hidden card"},
            ),
            session_file,
        )
    else:
        data: dict = {"card": str(card), "cardValue": card.value}
        if hand_value is not None:
            data["handValue"] = hand_value
        data["message"] = (
            f"{actor} dealt {card} — hand value: {hand_value}"
            if hand_value is not None
            else f"{actor} dealt {card} — card value: {card.value}"
        )
        _emit(
            GameEvent(
                eventType="CardDealt",
                sessionId=session_id,
                handId=hand_id,
                actor=actor,
                data=data,
            ),
            session_file,
        )


def _play_player_turn(
    player: Player,
    player_hand: Hand,
    shoe: Deck,
    session_id: str,
    hand_id: str,
    session_file: Path,
) -> None:
    """Run the hit/stand loop for a single player."""
    while not player_hand.is_bust:
        action = player.strategy(player_hand)
        if action not in ("hit", "stand"):
            raise ValueError(f"Unknown strategy action: {action!r}. Must be 'hit' or 'stand'.")
        if action == "stand":
            _emit(
                GameEvent(
                    eventType="StandDeclared",
                    sessionId=session_id,
                    handId=hand_id,
                    actor=player.name,
                    data={
                        "handValue": player_hand.value,
                        "message": f"Player {player.name} stands on {player_hand.value}",
                    },
                ),
                session_file,
            )
            break
        card = shoe.deal()
        player_hand.cards.append(card)
        _emit(
            GameEvent(
                eventType="CardDrawn",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "card": str(card),
                    "handValue": player_hand.value,
                    "message": (
                        f"Player {player.name} hits: {card} — hand value: {player_hand.value}"
                    ),
                },
            ),
            session_file,
        )

    if player_hand.is_bust:
        _emit(
            GameEvent(
                eventType="HandBust",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "handValue": player_hand.value,
                    "message": f"Player {player.name} busts with {player_hand.value}",
                },
            ),
            session_file,
        )


def _play_dealer_turn(
    dealer_hand: Hand,
    shoe: Deck,
    dealer_hits_soft17: bool,
    session_id: str,
    hand_id: str,
    session_file: Path,
    table: Table,
) -> None:
    """Run the dealer hit/stand loop and emit events."""
    revealed = table.dealer.reveal_hole_card(dealer_hand)
    _emit(
        GameEvent(
            eventType="HoleCardRevealed",
            sessionId=session_id,
            handId=hand_id,
            actor="Dealer",
            data={
                "card": str(revealed),
                "handValue": dealer_hand.value,
                "message": (f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}"),
            },
        ),
        session_file,
    )

    while not dealer_hand.is_bust:
        hit = dealer_hand.value <= 16 or (dealer_hits_soft17 and _is_soft_17(dealer_hand))
        if not hit:
            _emit(
                GameEvent(
                    eventType="StandDeclared",
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
        card = shoe.deal()
        dealer_hand.cards.append(card)
        _emit(
            GameEvent(
                eventType="CardDrawn",
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
        _emit(
            GameEvent(
                eventType="HandBust",
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


def _resolve_player(
    player: Player,
    player_hand: Hand,
    dealer_hand: Hand,
    blackjack_payout: float,
    session_id: str,
    hand_id: str,
    session_file: Path,
) -> None:
    """Resolve one player's hand against the dealer and emit payout events."""
    pv = player_hand.value
    dv = dealer_hand.value
    player_bj = player_hand.is_blackjack
    dealer_bj = dealer_hand.is_blackjack
    player_bust = player_hand.is_bust
    dealer_bust = dealer_hand.is_bust

    if player_bust:
        _emit(
            GameEvent(
                eventType="HandResolved",
                sessionId=session_id,
                handId=hand_id,
                data={
                    "result": "player_bust",
                    "message": f"{player.name} busts with {player_hand.value}",
                },
            ),
            session_file,
        )
        _emit_wallet(player, session_id, hand_id, session_file)
        return

    if player_bj and dealer_bj:
        _emit(
            GameEvent(
                eventType="HandResolved",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={"result": "push", "message": "Push — both have blackjack"},
            ),
            session_file,
        )
        player.receive_payout(player.bet)
        _emit_payout(player, player.bet, "push", session_id, hand_id, session_file)

    elif player_bj:
        payout = player.bet + player.bet * blackjack_payout
        _emit(
            GameEvent(
                eventType="HandResolved",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "result": "player_blackjack",
                    "message": f"Player {player.name} blackjack — pays {blackjack_payout}:1",
                },
            ),
            session_file,
        )
        player.receive_payout(payout)
        _emit_payout(player, payout, "blackjack", session_id, hand_id, session_file)

    elif dealer_bj:
        _emit(
            GameEvent(
                eventType="HandResolved",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "result": "dealer_blackjack",
                    "message": f"Dealer blackjack — player {player.name} loses",
                },
            ),
            session_file,
        )

    elif dealer_bust or pv > dv:
        payout = player.bet * 2
        _emit(
            GameEvent(
                eventType="HandResolved",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "result": "player_wins",
                    "message": (
                        f"Player {player.name} wins — "
                        + ("dealer busts" if dealer_bust else f"player {pv} beats dealer {dv}")
                    ),
                },
            ),
            session_file,
        )
        player.receive_payout(payout)
        _emit_payout(player, payout, "win", session_id, hand_id, session_file)

    elif dv > pv:
        _emit(
            GameEvent(
                eventType="HandResolved",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={
                    "result": "dealer_wins",
                    "message": (f"Dealer wins — dealer {dv} beats player {player.name} {pv}"),
                },
            ),
            session_file,
        )

    else:
        _emit(
            GameEvent(
                eventType="HandResolved",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={"result": "push", "message": f"Push — both have {pv}"},
            ),
            session_file,
        )
        player.receive_payout(player.bet)
        _emit_payout(player, player.bet, "push", session_id, hand_id, session_file)

    _emit_wallet(player, session_id, hand_id, session_file)


def _emit_payout(
    player: Player,
    amount: float,
    reason: str,
    session_id: str,
    hand_id: str,
    session_file: Path,
) -> None:
    _emit(
        GameEvent(
            eventType="PayoutMade",
            sessionId=session_id,
            handId=hand_id,
            actor=player.name,
            data={
                "amount": amount,
                "reason": reason,
                "message": f"Player {player.name} receives {amount:g} UoM — {reason}",
            },
        ),
        session_file,
    )


def _emit_wallet(player: Player, session_id: str, hand_id: str, session_file: Path) -> None:
    _emit(
        GameEvent(
            eventType="WalletUpdated",
            sessionId=session_id,
            handId=hand_id,
            actor=player.name,
            data={
                "wallet": player.wallet,
                "message": f"Player {player.name} wallet: {player.wallet:g} UoM",
            },
        ),
        session_file,
    )
    if player.wallet == 0.0:
        _emit(
            GameEvent(
                eventType="WalletEmpty",
                sessionId=session_id,
                handId=hand_id,
                actor=player.name,
                data={"message": f"Player {player.name} wallet reached 0 UoM"},
            ),
            session_file,
        )


def _emit_player_left(player: Player, reason: str, session_id: str, session_file: Path) -> None:
    _emit(
        GameEvent(
            eventType="PlayerLeft",
            sessionId=session_id,
            actor=player.name,
            data={
                "reason": reason,
                "message": f"Player {player.name} leaves — {reason}",
            },
        ),
        session_file,
    )


def play_table_session(
    table: Table,
    cut_card: int = 39,
    seed: int | None = None,
    max_hands: int | None = None,
) -> None:
    """Play a multiplayer blackjack session at the given table."""
    shoe_size = 52 * table.numDecks
    if cut_card < 1 or cut_card >= shoe_size:
        raise ValueError(f"cut_card must be between 1 and {shoe_size - 1}, got {cut_card}")
    if max_hands is not None and max_hands < 1:
        raise ValueError(f"max_hands must be at least 1, got {max_hands}")

    session_id = str(uuid4())
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    session_file = Path(f"logs/blackjack-{timestamp}-{session_id[-8:]}.jsonl")

    # --- Setup ---
    _emit(
        GameEvent(
            eventType="TableOpened",
            sessionId=session_id,
            data={
                "tableId": table.tableId,
                "maxSeats": table.maxSeats,
                "numDecks": table.numDecks,
                "minBet": table.minBet,
                "maxBet": table.maxBet,
                "message": (
                    f"Table {table.tableId} opened — {table.numDecks} deck(s), "
                    f"seats: {table.maxSeats}"
                ),
            },
        ),
        session_file,
    )
    _emit(
        GameEvent(
            eventType="SessionOpened",
            sessionId=session_id,
            data={
                "players": [p.name for p in table.players],
                "message": (
                    f"Session started — {len(table.players)} player(s): "
                    + ", ".join(p.name for p in table.players)
                ),
            },
        ),
        session_file,
    )
    for player in table.players:
        _emit(
            GameEvent(
                eventType="PlayerSeated",
                sessionId=session_id,
                actor=player.name,
                data={
                    "wallet": player.wallet,
                    "message": f"Player {player.name} seated — wallet: {player.wallet:g} UoM",
                },
            ),
            session_file,
        )

    shoe = _build_shoe(table.numDecks, seed)
    _emit(
        GameEvent(
            eventType="ShoeShuffled",
            sessionId=session_id,
            data={
                "deckSize": len(shoe),
                "message": f"Shuffled {len(shoe)}-card shoe",
            },
        ),
        session_file,
    )

    # Working copy of seated players (removed when wallet hits 0)
    active_players: list[Player] = list(table.players)
    hand_number = 0
    dealer_hits_soft17 = table.houseRules.dealerHitsOnSoft17
    blackjack_payout = table.houseRules.blackjackPayout

    while active_players:
        hand_number += 1
        hand_id = str(uuid4())

        _emit(
            GameEvent(
                eventType="HandStarted",
                sessionId=session_id,
                handId=hand_id,
                data={
                    "handNumber": hand_number,
                    "wallets": {p.name: p.wallet for p in active_players},
                    "message": (
                        f"Hand {hand_number} — "
                        + ", ".join(f"{p.name}: {p.wallet:g} UoM" for p in active_players)
                    ),
                },
            ),
            session_file,
        )

        # Place bets
        for player in active_players:
            player.place_bet()
            _emit(
                GameEvent(
                    eventType="BetPlaced",
                    sessionId=session_id,
                    handId=hand_id,
                    actor=player.name,
                    data={
                        "bet": player.bet,
                        "wallet": player.wallet,
                        "message": (
                            f"Player {player.name} bets {player.bet:g} UoM"
                            f" — wallet: {player.wallet:g} UoM"
                        ),
                    },
                ),
                session_file,
            )

        # Deal initial cards
        player_hands: dict[str, Hand] = {}
        for player in active_players:
            ph = _deal_player_hand(shoe)
            player_hands[player.name] = ph
            _emit_card_dealt(ph.cards[0], player.name, None, session_id, hand_id, session_file)
            _emit_card_dealt(ph.cards[1], player.name, ph.value, session_id, hand_id, session_file)

        dealer_hand = _deal_dealer_hand(shoe)
        _emit_card_dealt(dealer_hand.cards[0], "Dealer", None, session_id, hand_id, session_file)
        _emit_card_dealt(
            dealer_hand.cards[1],
            "Dealer",
            None,
            session_id,
            hand_id,
            session_file,
            is_hidden=True,
        )

        # Check for dealer blackjack before players act (peek)
        dealer_bj = dealer_hand.is_blackjack

        # Player turns in seat order
        for player in active_players:
            ph = player_hands[player.name]
            if not ph.is_blackjack:
                _play_player_turn(player, ph, shoe, session_id, hand_id, session_file)

        # Dealer turn — only if at least one player hasn't busted
        any_not_bust = any(not player_hands[p.name].is_bust for p in active_players)
        if any_not_bust and not dealer_bj:
            _play_dealer_turn(
                dealer_hand,
                shoe,
                dealer_hits_soft17,
                session_id,
                hand_id,
                session_file,
                table,
            )
        elif dealer_bj:
            # Reveal hole card even if dealer blackjack
            revealed = table.dealer.reveal_hole_card(dealer_hand)
            _emit(
                GameEvent(
                    eventType="HoleCardRevealed",
                    sessionId=session_id,
                    handId=hand_id,
                    actor="Dealer",
                    data={
                        "card": str(revealed),
                        "handValue": dealer_hand.value,
                        "message": (
                            f"Dealer reveals: {revealed} — hand value: {dealer_hand.value}"
                        ),
                    },
                ),
                session_file,
            )

        # Resolve each player
        for player in active_players:
            _resolve_player(
                player,
                player_hands[player.name],
                dealer_hand,
                blackjack_payout,
                session_id,
                hand_id,
                session_file,
            )

        # Remove busted wallets
        broke: list[Player] = [p for p in active_players if p.wallet == 0.0]
        for player in broke:
            _emit_player_left(player, "no funds", session_id, session_file)
            active_players.remove(player)

        if not active_players:
            break

        # Cut card check
        if len(shoe) <= max(cut_card, 4):
            _emit(
                GameEvent(
                    eventType="CutCardReached",
                    sessionId=session_id,
                    data={"message": "Cut card reached — reshuffling shoe"},
                ),
                session_file,
            )
            new_seed = seed + hand_number if seed is not None else None
            shoe = _build_shoe(table.numDecks, new_seed)
            _emit(
                GameEvent(
                    eventType="ShoeShuffled",
                    sessionId=session_id,
                    data={
                        "deckSize": len(shoe),
                        "message": f"Shuffled {len(shoe)}-card shoe",
                    },
                ),
                session_file,
            )

        # max_hands termination
        if max_hands is not None and hand_number >= max_hands:
            for player in list(active_players):
                _emit_player_left(player, "max hands reached", session_id, session_file)
            active_players.clear()
            break

    _emit(
        GameEvent(
            eventType="SessionClosed",
            sessionId=session_id,
            data={
                "handsPlayed": hand_number,
                "reason": "max hands reached"
                if (max_hands is not None and hand_number >= max_hands)
                else "no players remaining",
                "message": (f"Session closed — hands played: {hand_number}"),
            },
        ),
        session_file,
    )
    _emit(
        GameEvent(
            eventType="TableClosed",
            sessionId=session_id,
            data={
                "tableId": table.tableId,
                "message": f"Table {table.tableId} closed",
            },
        ),
        session_file,
    )
