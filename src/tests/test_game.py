"""Tests for src/game.py — deterministic via seeded deck.

Seed reference (stand strategy unless noted):
  seed=0  → dealer bust          (player wins +1 UoM)
  seed=2  → dealer wins          (player loses -1 UoM)
  seed=9  → dealer blackjack only (player loses -1 UoM)
  seed=19 → push                 (wallet unchanged)
  seed=49 → player blackjack only (pays 3:2, +1.5 UoM)
  seed=498 → both blackjack      (push, wallet unchanged)
"""

import logging

import pytest

from src.cards import Deck
from src.game import play_hand, play_session
from src.hand import Hand
from src.player import Player


def _stand_strategy(hand: Hand) -> str:
    return "stand"


def _hit_strategy(hand: Hand) -> str:
    return "hit"


def _make_deck(seed: int) -> Deck:
    deck = Deck()
    deck.shuffle(seed=seed)
    return deck


# ---------------------------------------------------------------------------
# play_hand() — existing behaviour (refactored to pass deck explicitly)
# ---------------------------------------------------------------------------


def test_play_hand_deducts_bet_at_start(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs BET event and deducts 1 UoM."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[BET]" in caplog.text
    assert p.wallet == 99.0


def test_play_hand_logs_deck_shuffle(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand does not log deck shuffle — that belongs to the caller."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[DECK]" not in caplog.text


def test_play_hand_logs_deal_events(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs DEAL events for initial cards."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[DEAL]" in caplog.text


def test_play_hand_logs_outcome(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs an OUTCOME event."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[OUTCOME]" in caplog.text


def test_play_hand_logs_wallet(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs WALLET event."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[WALLET]" in caplog.text


def test_play_hand_player_bust_logs_bust(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs BUST when player always hits until bust."""
    p = Player(name="Alice", strategy=_hit_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[BUST] Player busts" in caplog.text
    assert "[OUTCOME]" not in caplog.text


def test_play_hand_wallet_zero_logs_leave_not_table(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs [LEAVE] (not [TABLE]) when wallet reaches 0 after a loss."""
    p = Player(name="Alice", strategy=_stand_strategy)
    p.wallet = 1.0
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert p.wallet == 0.0
    assert "[LEAVE]" in caplog.text
    assert "[TABLE]" not in caplog.text


def test_play_hand_player_blackjack_only_pays_3_to_2(caplog: pytest.LogCaptureFixture) -> None:
    """Player blackjack (dealer does not have blackjack) pays 3:2 — wallet: 100 → 101.5."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(49))
    assert "[OUTCOME] Player blackjack — pays 3:2" in caplog.text
    assert p.wallet == 101.5


def test_play_hand_both_blackjack_is_push(caplog: pytest.LogCaptureFixture) -> None:
    """Both player and dealer have blackjack — outcome is a push, wallet unchanged."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(498))
    assert "[OUTCOME] Push — both have blackjack" in caplog.text
    assert p.wallet == 100.0


def test_play_hand_push_returns_bet(caplog: pytest.LogCaptureFixture) -> None:
    """Push returns the bet — wallet is unchanged at 100 UoM."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(19))
    assert "Push" in caplog.text
    assert p.wallet == 100.0


def test_play_hand_dealer_bust_player_wins(caplog: pytest.LogCaptureFixture) -> None:
    """Dealer bust results in player winning 1 UoM — wallet goes from 100 to 101."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(0))
    assert "[BUST] Dealer busts" in caplog.text
    assert p.wallet == 101.0


def test_play_hand_invalid_strategy_raises() -> None:
    """Strategy returning an unknown action raises ValueError."""

    def bad_strategy(hand: Hand) -> str:
        return "double"

    p = Player(name="Alice", strategy=bad_strategy)
    with pytest.raises(ValueError, match="Unknown strategy action"):
        play_hand(p, _make_deck(2))


def test_play_hand_deterministic_same_seed(caplog: pytest.LogCaptureFixture) -> None:
    """Same seed produces identical log output twice."""
    p1 = Player(name="Alice", strategy=_stand_strategy)
    p2 = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p1, _make_deck(7))
    log1 = caplog.text
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p2, _make_deck(7))
    log2 = caplog.text
    assert log1 == log2


def test_play_hand_dealer_blackjack_only_player_loses(caplog: pytest.LogCaptureFixture) -> None:
    """Dealer blackjack (player does not have blackjack) — player loses bet, wallet: 99."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(9))
    assert "[REVEAL]" in caplog.text
    assert "[OUTCOME] Dealer blackjack — player loses" in caplog.text
    assert p.wallet == 99.0


def test_play_hand_logs_reveal(caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs REVEAL event for dealer hole card (non-blackjack hand)."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[REVEAL]" in caplog.text


# --- WALLET / TABLE logging across all exit paths ---


def test_wallet_logged_on_player_blackjack_exit(caplog: pytest.LogCaptureFixture) -> None:
    """WALLET is logged on the player-blackjack exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(49))
    assert "[WALLET] Player wallet: 101.5 UoM" in caplog.text


def test_wallet_logged_on_both_blackjack_exit(caplog: pytest.LogCaptureFixture) -> None:
    """WALLET is logged on the both-blackjack push exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(498))
    assert "[WALLET] Player wallet: 100 UoM" in caplog.text


def test_wallet_logged_on_dealer_blackjack_exit(caplog: pytest.LogCaptureFixture) -> None:
    """WALLET is logged on the dealer-blackjack exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(9))
    assert "[WALLET] Player wallet: 99 UoM" in caplog.text


def test_wallet_logged_on_player_bust_exit(caplog: pytest.LogCaptureFixture) -> None:
    """WALLET is logged on the player-bust exit path."""
    p = Player(name="Alice", strategy=_hit_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[WALLET] Player wallet: 99 UoM" in caplog.text


def test_wallet_logged_on_dealer_bust_exit(caplog: pytest.LogCaptureFixture) -> None:
    """WALLET is logged on the dealer-bust exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(0))
    assert "[WALLET] Player wallet: 101 UoM" in caplog.text


def test_wallet_logged_on_final_outcome_exit(caplog: pytest.LogCaptureFixture) -> None:
    """WALLET is logged on the final-outcome (dealer wins) exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[WALLET] Player wallet: 99 UoM" in caplog.text


def test_leave_logged_on_dealer_blackjack_exit_when_wallet_zero(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """LEAVE is logged on dealer-blackjack exit when wallet reaches 0."""
    p = Player(name="Alice", strategy=_stand_strategy)
    p.wallet = 1.0
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(9))
    assert p.wallet == 0.0
    assert "[LEAVE] Player leaves — wallet reached 0 UoM" in caplog.text


def test_deal_log_first_player_card_says_card_value(caplog: pytest.LogCaptureFixture) -> None:
    """First player DEAL log uses 'card value' not 'hand value'."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "card value" in caplog.text.split("[DEAL]")[1]


def test_deal_log_dealer_upcard_says_card_value(caplog: pytest.LogCaptureFixture) -> None:
    """Dealer upcard DEAL log uses 'card value' not 'hand value'."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    dealer_deal_log = [
        line for line in caplog.text.split("\n") if "[DEAL]" in line and "Dealer shows" in line
    ]
    assert len(dealer_deal_log) == 1
    assert "card value" in dealer_deal_log[0]


# ---------------------------------------------------------------------------
# play_hand() — PAYOUT events (2c)
# ---------------------------------------------------------------------------


def test_play_hand_payout_logged_on_blackjack(caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] logged with blackjack 3:2 message when player hits blackjack."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(49))
    assert "[PAYOUT] Player receives 2.5 UoM — blackjack 3:2" in caplog.text


def test_play_hand_payout_logged_on_win(caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] logged with win message when player wins 1:1."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(0))
    assert "[PAYOUT] Player receives 2 UoM — win" in caplog.text


def test_play_hand_payout_logged_on_push(caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] logged with push message on a push."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(19))
    assert "[PAYOUT] Player receives 1 UoM — push" in caplog.text


def test_play_hand_no_payout_on_dealer_wins(caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] not logged when dealer wins (player loses bet)."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[PAYOUT]" not in caplog.text


def test_play_hand_no_payout_on_player_bust(caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] not logged when player busts."""
    p = Player(name="Alice", strategy=_hit_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, _make_deck(2))
    assert "[PAYOUT]" not in caplog.text


# ---------------------------------------------------------------------------
# play_session() — Step 3
# ---------------------------------------------------------------------------


def test_play_session_logs_open(caplog: pytest.LogCaptureFixture) -> None:
    """[OPEN] logged at session start with player name, max hands, starting wallet."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=2)
    assert (
        "[OPEN] Session started — player: Alice, max hands: 1, starting wallet: 100 UoM"
        in caplog.text
    )


def test_play_session_logs_shuffle_at_start(caplog: pytest.LogCaptureFixture) -> None:
    """[SHUFFLE] logged at session start after deck creation."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=2)
    assert "[SHUFFLE] Shuffled 52-card deck" in caplog.text


def test_play_session_logs_hand_each_hand(caplog: pytest.LogCaptureFixture) -> None:
    """[HAND] logged at start of each hand with hand number and wallet."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=2, seed=2)
    assert "[HAND] Hand 1 of 2" in caplog.text
    assert "[HAND] Hand 2 of 2" in caplog.text


def test_play_session_terminates_on_max_hands(caplog: pytest.LogCaptureFixture) -> None:
    """Session ends after max_hands — [LEAVE] and [CLOSE] logged with reason."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=2, seed=2)
    assert "[LEAVE] Player leaves — max hands reached" in caplog.text
    assert "reason: max hands reached" in caplog.text


def test_play_session_terminates_on_wallet_zero(caplog: pytest.LogCaptureFixture) -> None:
    """Session ends when wallet reaches 0 — [LEAVE] and [CLOSE] logged with reason."""
    p = Player(name="Alice", strategy=_stand_strategy)
    p.wallet = 1.0
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=10, seed=2)
    assert "[LEAVE] Player leaves — no funds" in caplog.text
    assert "reason: no funds" in caplog.text


def test_play_session_logs_close_with_summary(caplog: pytest.LogCaptureFixture) -> None:
    """[CLOSE] contains hands played, final wallet, and reason."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=2)
    assert "[CLOSE] Session closed — hands played: 1" in caplog.text


def test_play_session_logs_cut_and_reshuffle(caplog: pytest.LogCaptureFixture) -> None:
    """[CUT] and second [SHUFFLE] logged when deck falls to or below cut_card threshold."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        # cut_card=51: deck drops below 51 after any hand (52 - 4+ dealt cards)
        play_session(p, max_hands=2, cut_card=51, seed=2)
    assert "[CUT] Cut card reached — reshuffling after this hand" in caplog.text
    assert caplog.text.count("[SHUFFLE] Shuffled 52-card deck") >= 2


def test_play_session_raises_on_invalid_max_hands() -> None:
    """ValueError raised if max_hands < 1."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with pytest.raises(ValueError, match="max_hands"):
        play_session(p, max_hands=0)


def test_play_session_raises_on_invalid_cut_card_low() -> None:
    """ValueError raised if cut_card < 1."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with pytest.raises(ValueError, match="cut_card"):
        play_session(p, cut_card=0)


def test_play_session_raises_on_invalid_cut_card_high() -> None:
    """ValueError raised if cut_card >= 52."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with pytest.raises(ValueError, match="cut_card"):
        play_session(p, cut_card=52)


def test_play_session_payout_logged_on_win(caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] logged when player wins a hand during session."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=0)
    assert "[PAYOUT] Player receives 2 UoM — win" in caplog.text


def test_play_session_payout_logged_on_blackjack(caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] logged when player hits blackjack during session."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=49)
    assert "[PAYOUT] Player receives 2.5 UoM — blackjack 3:2" in caplog.text


def test_play_session_payout_logged_on_push(caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] logged on push during session."""
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=19)
    assert "[PAYOUT] Player receives 1 UoM — push" in caplog.text
