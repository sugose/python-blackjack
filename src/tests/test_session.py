"""Tests for play_table_session() — multi-player session loop."""

import json
from pathlib import Path

import pytest

from src.dealer import Dealer
from src.player import Player
from src.session import play_table_session
from src.table import HouseRules, Table


def _stand_strategy(hand):  # noqa: ANN001
    return "stand"


def _always_hit(hand):  # noqa: ANN001
    return "hit"


def _make_player(name: str = "Alice", wallet: float = 100.0, strategy=None) -> Player:
    return Player(name=name, strategy=strategy or _stand_strategy, wallet=wallet)


def _make_table(
    players: list[Player] | None = None,
    max_seats: int = 7,
    num_decks: int = 1,
    min_bet: float = 1.0,
    max_bet: float = 100.0,
    dealer_hits_soft17: bool = False,
    blackjack_payout: float = 1.5,
) -> Table:
    return Table(
        tableId="t-abc",
        maxSeats=max_seats,
        minBet=min_bet,
        maxBet=max_bet,
        numDecks=num_decks,
        players=players or [_make_player()],
        dealer=Dealer(),
        houseRules=HouseRules(
            blackjackPayout=blackjack_payout,
            dealerHitsOnSoft17=dealer_hits_soft17,
        ),
    )


def _read_events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


class TestValidation:
    def test_cut_card_less_than_1_raises(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        with pytest.raises(ValueError, match="cut_card"):
            play_table_session(table, cut_card=0, max_hands=1)

    def test_cut_card_ge_shoe_size_raises(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table(num_decks=1)
        with pytest.raises(ValueError, match="cut_card"):
            play_table_session(table, cut_card=52, max_hands=1)

    def test_cut_card_multi_deck_boundary(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table(num_decks=2)
        with pytest.raises(ValueError, match="cut_card"):
            play_table_session(table, cut_card=104, max_hands=1)

    def test_max_hands_zero_raises(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        with pytest.raises(ValueError, match="max_hands"):
            play_table_session(table, max_hands=0)

    def test_max_hands_negative_raises(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        with pytest.raises(ValueError, match="max_hands"):
            play_table_session(table, max_hands=-1)


class TestSetupEvents:
    def test_table_opened_first_event(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        assert events[0]["eventType"] == "TableOpened"

    def test_session_opened_second_event(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        assert events[1]["eventType"] == "SessionOpened"

    def test_player_seated_events_after_session_opened(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        players = [_make_player("Alice"), _make_player("Bob")]
        table = _make_table(players=players)
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        seated = [e for e in events if e["eventType"] == "PlayerSeated"]
        assert len(seated) == 2
        assert seated[0]["actor"] == "Alice"
        assert seated[1]["actor"] == "Bob"

    def test_shoe_shuffled_after_setup(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table(num_decks=2)
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        shoe_event = next(e for e in events if e["eventType"] == "ShoeShuffled")
        assert shoe_event["data"]["deckSize"] == 104  # 2 × 52

    def test_shoe_size_single_deck(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table(num_decks=1)
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        shoe_event = next(e for e in events if e["eventType"] == "ShoeShuffled")
        assert shoe_event["data"]["deckSize"] == 52


class TestHandEvents:
    def test_hand_started_emitted_per_hand(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        play_table_session(table, seed=42, max_hands=3)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        hand_starts = [e for e in events if e["eventType"] == "HandStarted"]
        assert len(hand_starts) == 3

    def test_hand_started_contains_wallet_info(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table(players=[_make_player("Alice", wallet=50.0)])
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        hs = next(e for e in events if e["eventType"] == "HandStarted")
        assert "wallets" in hs["data"]

    def test_players_act_before_dealer_per_hand(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        players = [_make_player("Alice"), _make_player("Bob")]
        table = _make_table(players=players)
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        hand_id = next(e for e in events if e["eventType"] == "HandStarted")["handId"]
        hand_events = [e for e in events if e.get("handId") == hand_id]
        actors = [e.get("actor") for e in hand_events if e.get("actor") is not None]
        # Alice and Bob should appear before Dealer
        dealer_idx = next((i for i, a in enumerate(actors) if a == "Dealer"), None)
        alice_idx = next((i for i, a in enumerate(actors) if a == "Alice"), None)
        bob_idx = next((i for i, a in enumerate(actors) if a == "Bob"), None)
        assert alice_idx is not None
        assert bob_idx is not None
        assert dealer_idx is not None
        assert alice_idx < dealer_idx
        assert bob_idx < dealer_idx

    def test_alice_acts_before_bob_seat_order(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        players = [_make_player("Alice"), _make_player("Bob")]
        table = _make_table(players=players)
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        hand_id = next(e for e in events if e["eventType"] == "HandStarted")["handId"]
        hand_events = [e for e in events if e.get("handId") == hand_id]
        actors = [e.get("actor") for e in hand_events]
        alice_idx = next(i for i, a in enumerate(actors) if a == "Alice")
        bob_idx = next(i for i, a in enumerate(actors) if a == "Bob")
        assert alice_idx < bob_idx

    def test_hand_resolved_player_bust_emitted(self, tmp_path: Path, monkeypatch) -> None:
        # Regression guard: HandResolved with result "player_bust" must fire when player busts.
        # seed=0 with always-hit strategy causes Alice to bust on hand 1.
        monkeypatch.chdir(tmp_path)
        table = _make_table(players=[_make_player("Alice", strategy=_always_hit)])
        play_table_session(table, seed=0, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        bust_resolved = next(
            (
                e
                for e in events
                if e["eventType"] == "HandResolved" and e["data"].get("result") == "player_bust"
            ),
            None,
        )
        assert bust_resolved is not None, "HandResolved with result='player_bust' not emitted"


class TestTermination:
    def test_table_closed_is_last_event(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        play_table_session(table, seed=42, max_hands=2)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        assert events[-1]["eventType"] == "TableClosed"

    def test_session_closed_before_table_closed(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        play_table_session(table, seed=42, max_hands=2)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        types = [e["eventType"] for e in events]
        assert "SessionClosed" in types
        assert types.index("SessionClosed") < types.index("TableClosed")

    def test_max_hands_termination_emits_player_left_for_all(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        players = [_make_player("Alice"), _make_player("Bob")]
        table = _make_table(players=players)
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        left = [e for e in events if e["eventType"] == "PlayerLeft"]
        left_actors = {e["actor"] for e in left}
        assert "Alice" in left_actors
        assert "Bob" in left_actors

    def test_player_left_when_wallet_zero(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        # Player with bet=1, wallet=1 always stands and may lose or push.
        # Use always-hit strategy on a seeded deck where player busts immediately
        # to guarantee wallet hits 0 quickly.
        # Easier: give player wallet=1.0, bet=1.0, always stand.
        # After 1 loss, wallet=0. Seed chosen to cause a loss.
        player = Player(name="Broke", strategy=_stand_strategy, wallet=1.0)
        player.bet = 1.0
        table = _make_table(players=[player], max_seats=7)
        # Run enough hands that wallet hits 0 eventually
        play_table_session(table, seed=99, max_hands=50)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        wallet_empty = [e for e in events if e["eventType"] == "WalletEmpty"]
        player_left = [e for e in events if e["eventType"] == "PlayerLeft"]
        assert len(wallet_empty) >= 1
        assert any(e["actor"] == "Broke" for e in player_left)

    def test_natural_termination_no_players_remaining(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        player = Player(name="Broke", strategy=_stand_strategy, wallet=1.0)
        player.bet = 1.0
        table = _make_table(players=[player], max_seats=7)
        play_table_session(table, seed=99, max_hands=50)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        types = [e["eventType"] for e in events]
        assert "SessionClosed" in types
        assert "TableClosed" in types

    def test_session_closed_reason_max_hands(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        play_table_session(table, seed=42, max_hands=2)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        sc = next(e for e in events if e["eventType"] == "SessionClosed")
        assert sc["data"]["reason"] == "max hands reached"

    def test_session_closed_contains_hands_played(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table()
        play_table_session(table, seed=42, max_hands=3)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        sc = next(e for e in events if e["eventType"] == "SessionClosed")
        assert sc["data"]["handsPlayed"] == 3


class TestCutCard:
    def test_cut_card_triggers_reshuffle(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        # With cut_card=39 and 1 deck, after ~2-3 hands the deck drops below 39
        table = _make_table(num_decks=1)
        play_table_session(table, seed=42, cut_card=39, max_hands=10)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        cut_events = [e for e in events if e["eventType"] == "CutCardReached"]
        assert len(cut_events) >= 1

    def test_shoe_reshuffled_after_cut_card(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table(num_decks=1)
        play_table_session(table, seed=42, cut_card=39, max_hands=10)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        types = [e["eventType"] for e in events]
        cut_idx = types.index("CutCardReached")
        assert types[cut_idx + 1] == "ShoeShuffled"


class TestMultiDeck:
    def test_six_deck_shoe(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        table = _make_table(num_decks=6)
        play_table_session(table, seed=42, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        shoe_event = next(e for e in events if e["eventType"] == "ShoeShuffled")
        assert shoe_event["data"]["deckSize"] == 312  # 6 × 52


class TestHouseRulesBlackjackPayout:
    def test_blackjack_payout_applied_from_house_rules(self, tmp_path: Path, monkeypatch) -> None:
        # seed=5 is pinned: produces player blackjack on hand 1 with a single 1-deck shoe.
        # bet=1.0, payout = 1.0 + 1.0 * 1.2 = 2.2 UoM.
        monkeypatch.chdir(tmp_path)
        player = Player(name="Alice", strategy=_stand_strategy, wallet=10.0)
        rules = HouseRules(blackjackPayout=1.2, dealerHitsOnSoft17=False)
        table = Table(
            tableId="t-payout",
            maxSeats=7,
            minBet=1.0,
            maxBet=100.0,
            numDecks=1,
            players=[player],
            dealer=Dealer(),
            houseRules=rules,
        )
        play_table_session(table, seed=5, max_hands=1)
        events = _read_events(next(tmp_path.glob("logs/*.jsonl")))
        bj_event = next(
            (
                e
                for e in events
                if e["eventType"] == "HandResolved"
                and e["data"].get("result") == "player_blackjack"
            ),
            None,
        )
        # seed=5 is pinned; update if card ordering ever changes
        assert bj_event is not None
        payout_event = next(e for e in events if e["eventType"] == "PayoutMade")
        assert payout_event["data"]["amount"] == pytest.approx(2.2)
