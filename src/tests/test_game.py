"""Tests for src/game.py — deterministic via seeded deck.

Seed reference (stand strategy unless noted):
  seed=0  → dealer bust          (player wins +1 UoM)
  seed=2  → dealer wins          (player loses -1 UoM)
  seed=9  → dealer blackjack only (player loses -1 UoM)
  seed=19 → push                 (wallet unchanged)
  seed=49 → player blackjack only (pays 3:2, +1.5 UoM)
  seed=498 → both blackjack      (push, wallet unchanged)
"""

import json
import logging
from pathlib import Path
from uuid import uuid4

import pytest

from src.cards import Deck
from src.game import play_hand, play_hand_standalone, play_session
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


def _ctx(tmp_path: Path, seed: int = 2) -> tuple[str, Path, Deck]:
    """Return (session_id, session_file, seeded deck) for play_hand() calls."""
    return str(uuid4()), tmp_path / "test.jsonl", _make_deck(seed)


# ---------------------------------------------------------------------------
# play_hand() — core behaviour
# ---------------------------------------------------------------------------


def test_play_hand_deducts_bet_at_start(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs BET event and deducts 1 UoM."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[BET]" in caplog.text
    assert p.wallet == 99.0


def test_play_hand_logs_deck_shuffle(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """play_hand does not log deck shuffle — that belongs to the caller."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[DECK]" not in caplog.text


def test_play_hand_logs_deal_events(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs DEAL events for initial cards."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[DEAL]" in caplog.text


def test_play_hand_logs_outcome(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs an OUTCOME event."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[OUTCOME]" in caplog.text


def test_play_hand_logs_wallet(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs WALLET event."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[WALLET]" in caplog.text


def test_play_hand_player_bust_logs_bust(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs BUST when player always hits until bust."""
    p = Player(name="Alice", strategy=_hit_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[BUST]" in caplog.text
    assert "Player busts" in caplog.text
    assert "[OUTCOME]" not in caplog.text


def test_play_hand_wallet_zero_logs_leave_not_table(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """play_hand logs [LEAVE] (not [TABLE]) when wallet reaches 0 after a loss."""
    p = Player(name="Alice", strategy=_stand_strategy)
    p.wallet = 1.0
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert p.wallet == 0.0
    assert "[LEAVE]" in caplog.text
    assert "[TABLE]" not in caplog.text


def test_play_hand_player_blackjack_only_pays_3_to_2(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Player blackjack (dealer does not have blackjack) pays 3:2 — wallet: 100 → 101.5."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=49)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[OUTCOME]" in caplog.text
    assert "Player blackjack — pays 3:2" in caplog.text
    assert p.wallet == 101.5


def test_play_hand_both_blackjack_is_push(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Both player and dealer have blackjack — outcome is a push, wallet unchanged."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=498)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[OUTCOME]" in caplog.text
    assert "Push — both have blackjack" in caplog.text
    assert p.wallet == 100.0


def test_play_hand_push_returns_bet(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Push returns the bet — wallet is unchanged at 100 UoM."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=19)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "Push" in caplog.text
    assert p.wallet == 100.0


def test_play_hand_dealer_bust_player_wins(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Dealer bust results in player winning 1 UoM — wallet goes from 100 to 101."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=0)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[BUST]" in caplog.text
    assert "Dealer busts" in caplog.text
    assert p.wallet == 101.0


def test_play_hand_invalid_strategy_raises(tmp_path: Path) -> None:
    """Strategy returning an unknown action raises ValueError."""

    def bad_strategy(hand: Hand) -> str:
        return "double"

    p = Player(name="Alice", strategy=bad_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with pytest.raises(ValueError, match="Unknown strategy action"):
        play_hand(p, sid, sf, deck)


def test_play_hand_deterministic_same_seed(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Same seed and same session_id produce identical HRF event types in the same order."""
    session_id = "test-session-id-deterministic"
    p1 = Player(name="Alice", strategy=_stand_strategy)
    p2 = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p1, session_id, tmp_path / "s1.jsonl", _make_deck(7))
    types1 = [line.split("]")[0].lstrip() for line in caplog.text.splitlines() if "]" in line]
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p2, session_id, tmp_path / "s2.jsonl", _make_deck(7))
    types2 = [line.split("]")[0].lstrip() for line in caplog.text.splitlines() if "]" in line]
    assert types1 == types2


def test_play_hand_dealer_blackjack_only_player_loses(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Dealer blackjack (player does not have blackjack) — player loses bet, wallet: 99."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=9)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[REVEAL]" in caplog.text
    assert "Dealer blackjack — player loses" in caplog.text
    assert p.wallet == 99.0


def test_play_hand_logs_reveal(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """play_hand logs REVEAL event for dealer hole card (non-blackjack hand)."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[REVEAL]" in caplog.text


# --- WALLET / LEAVE logging across all exit paths ---


def test_wallet_logged_on_player_blackjack_exit(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WALLET is logged on the player-blackjack exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=49)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[WALLET]" in caplog.text
    assert "Player wallet: 101.5 UoM" in caplog.text


def test_wallet_logged_on_both_blackjack_exit(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WALLET is logged on the both-blackjack push exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=498)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[WALLET]" in caplog.text
    assert "Player wallet: 100 UoM" in caplog.text


def test_wallet_logged_on_dealer_blackjack_exit(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WALLET is logged on the dealer-blackjack exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=9)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[WALLET]" in caplog.text
    assert "Player wallet: 99 UoM" in caplog.text


def test_wallet_logged_on_player_bust_exit(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WALLET is logged on the player-bust exit path."""
    p = Player(name="Alice", strategy=_hit_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[WALLET]" in caplog.text
    assert "Player wallet: 99 UoM" in caplog.text


def test_wallet_logged_on_dealer_bust_exit(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WALLET is logged on the dealer-bust exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=0)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[WALLET]" in caplog.text
    assert "Player wallet: 101 UoM" in caplog.text


def test_wallet_logged_on_final_outcome_exit(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """WALLET is logged on the final-outcome (dealer wins) exit path."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[WALLET]" in caplog.text
    assert "Player wallet: 99 UoM" in caplog.text


def test_leave_logged_on_dealer_blackjack_exit_when_wallet_zero(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """LEAVE is logged on dealer-blackjack exit when wallet reaches 0."""
    p = Player(name="Alice", strategy=_stand_strategy)
    p.wallet = 1.0
    sid, sf, deck = _ctx(tmp_path, seed=9)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert p.wallet == 0.0
    assert "[LEAVE]" in caplog.text
    assert "Player leaves — wallet reached 0 UoM" in caplog.text


def test_deal_log_first_player_card_says_card_value(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """First player DEAL log uses 'card value' not 'hand value'."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    deal_lines = [line for line in caplog.text.splitlines() if "[DEAL]" in line]
    assert any("card value" in line for line in deal_lines[:2])


def test_deal_log_dealer_upcard_says_card_value(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Dealer upcard DEAL log uses 'card value' not 'hand value'."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    dealer_deal_lines = [
        line for line in caplog.text.splitlines() if "[DEAL]" in line and "Dealer shows" in line
    ]
    assert len(dealer_deal_lines) == 1
    assert "card value" in dealer_deal_lines[0]


# ---------------------------------------------------------------------------
# play_hand() — PAYOUT events
# ---------------------------------------------------------------------------


def test_play_hand_payout_logged_on_blackjack(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """[PAYOUT] logged with blackjack 3:2 message when player hits blackjack."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=49)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[PAYOUT]" in caplog.text
    assert "Player receives 2.5 UoM — blackjack 3:2" in caplog.text


def test_play_hand_payout_logged_on_win(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] logged with win message when player wins 1:1."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=0)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[PAYOUT]" in caplog.text
    assert "Player receives 2 UoM — win" in caplog.text


def test_play_hand_payout_logged_on_push(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """[PAYOUT] logged with push message on a push."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path, seed=19)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[PAYOUT]" in caplog.text
    assert "Player receives 1 UoM — push" in caplog.text


def test_play_hand_no_payout_on_dealer_wins(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """[PAYOUT] not logged when dealer wins (player loses bet)."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[PAYOUT]" not in caplog.text


def test_play_hand_no_payout_on_player_bust(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """[PAYOUT] not logged when player busts."""
    p = Player(name="Alice", strategy=_hit_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "[PAYOUT]" not in caplog.text


# ---------------------------------------------------------------------------
# play_hand() — new signature: JSONL output and HRF prefixes (PBI-1.3)
# ---------------------------------------------------------------------------


def test_play_hand_new_signature_writes_jsonl_file(tmp_path: Path) -> None:
    """play_hand creates a JSONL session file."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    play_hand(p, sid, sf, deck)
    assert sf.exists()


def test_play_hand_new_signature_jsonl_contains_bet_event(tmp_path: Path) -> None:
    """play_hand writes a BET event to the JSONL file."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    play_hand(p, sid, sf, deck)
    events = [json.loads(line) for line in sf.read_text(encoding="utf-8").splitlines()]
    bet_events = [e for e in events if e["eventType"] == "BET"]
    assert len(bet_events) == 1
    assert bet_events[0]["actor"] == "Alice"


def test_play_hand_new_signature_jsonl_session_id_matches(tmp_path: Path) -> None:
    """All JSONL events carry the session_id passed into play_hand."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    play_hand(p, sid, sf, deck)
    events = [json.loads(line) for line in sf.read_text(encoding="utf-8").splitlines()]
    assert all(e["sessionId"] == sid for e in events)


def test_play_hand_new_signature_hrf_includes_sess_prefix(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """HRF log lines include sess: prefix for all hand events."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert f"sess:{sid[-8:]}" in caplog.text


def test_play_hand_new_signature_hrf_includes_hand_prefix(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """HRF log lines include hand: prefix for hand-level events."""
    p = Player(name="Alice", strategy=_stand_strategy)
    sid, sf, deck = _ctx(tmp_path)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_hand(p, sid, sf, deck)
    assert "hand:" in caplog.text


def test_play_hand_standalone_creates_session_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """play_hand_standalone creates a JSONL file under logs/."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    play_hand_standalone(p, seed=2)
    jsonl_files = list((tmp_path / "logs").glob("*.jsonl"))
    assert len(jsonl_files) == 1


# ---------------------------------------------------------------------------
# play_session() — multi-hand session
# ---------------------------------------------------------------------------


def test_play_session_logs_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """[OPEN] logged at session start with player name, max hands, starting wallet."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=2)
    assert "[OPEN]" in caplog.text
    assert "Session started — player: Alice, max hands: 1, starting wallet: 100 UoM" in caplog.text


def test_play_session_logs_shuffle_at_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """[SHUFFLE] logged at session start after deck creation."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=2)
    assert "[SHUFFLE]" in caplog.text
    assert "Shuffled 52-card deck" in caplog.text


def test_play_session_logs_hand_each_hand(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """[HAND] logged at start of each hand with hand number and wallet."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=2, seed=2)
    assert "Hand 1 of 2" in caplog.text
    assert "Hand 2 of 2" in caplog.text


def test_play_session_terminates_on_max_hands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Session ends after max_hands — [LEAVE] and [CLOSE] logged with reason."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=2, seed=2)
    assert "[LEAVE]" in caplog.text
    assert "Player leaves — max hands reached" in caplog.text
    assert "reason: max hands reached" in caplog.text


def test_play_session_terminates_on_wallet_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Session ends when wallet reaches 0 — [LEAVE] and [CLOSE] logged with reason."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    p.wallet = 1.0
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=10, seed=2)
    assert "[LEAVE]" in caplog.text
    assert "Player leaves — no funds" in caplog.text
    assert "reason: no funds" in caplog.text


def test_play_session_logs_close_with_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """[CLOSE] contains hands played, final wallet, and reason."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=2)
    assert "[CLOSE]" in caplog.text
    assert "Session closed — hands played: 1" in caplog.text


def test_play_session_logs_cut_and_reshuffle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """[CUT] and second [SHUFFLE] logged when deck falls to or below cut_card threshold."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        # cut_card=51: deck drops below 51 after any hand (52 - 4+ dealt cards)
        play_session(p, max_hands=2, cut_card=51, seed=2)
    assert "[CUT]" in caplog.text
    assert "Cut card reached — reshuffling after this hand" in caplog.text
    assert caplog.text.count("Shuffled 52-card deck") >= 2


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


def test_play_session_payout_logged_on_win(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """[PAYOUT] logged when player wins a hand during session."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=0)
    assert "[PAYOUT]" in caplog.text
    assert "Player receives 2 UoM — win" in caplog.text


def test_play_session_payout_logged_on_blackjack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """[PAYOUT] logged when player hits blackjack during session."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=49)
    assert "[PAYOUT]" in caplog.text
    assert "Player receives 2.5 UoM — blackjack 3:2" in caplog.text


def test_play_session_payout_logged_on_push(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """[PAYOUT] logged on push during session."""
    monkeypatch.chdir(tmp_path)
    p = Player(name="Alice", strategy=_stand_strategy)
    with caplog.at_level(logging.INFO, logger="blackjack"):
        play_session(p, max_hands=1, seed=19)
    assert "[PAYOUT]" in caplog.text
    assert "Player receives 1 UoM — push" in caplog.text
