"""Tests for src/strategy.py — adapt() and human_strategy."""

from pathlib import Path

import pytest

from src.cards import Card
from src.dealer import Dealer
from src.hand import Hand
from src.player import Player
from src.session import play_table_session
from src.strategy import adapt, human_strategy
from src.table import HouseRules, Table


def _make_card(rank: str = "7", suit: str = "Hearts") -> Card:
    return Card(rank=rank, suit=suit)


def _make_hand(*ranks: str) -> Hand:
    return Hand([_make_card(r) for r in ranks])


class TestAdapt:
    def test_adapt_wraps_one_arg_strategy(self) -> None:
        """adapt() wraps a one-arg (Hand-only) strategy to the two-arg signature."""
        calls: list[Hand] = []

        def one_arg(hand: Hand) -> str:
            calls.append(hand)
            return "stand"

        adapted = adapt(one_arg)
        hand = _make_hand("7", "8")
        upcard = _make_card("6")
        result = adapted(hand, upcard)
        assert result == "stand"
        assert calls == [hand]

    def test_adapt_passes_through_two_arg_strategy(self) -> None:
        """adapt() returns a two-arg strategy callable that works correctly."""
        received: list = []

        def two_arg(hand: Hand, upcard: Card) -> str:
            received.append((hand, upcard))
            return "hit"

        adapted = adapt(two_arg)
        hand = _make_hand("5", "4")
        upcard = _make_card("Ace")
        result = adapted(hand, upcard)
        assert result == "hit"
        assert received == [(hand, upcard)]

    def test_adapt_fallback_on_uninspectable(self) -> None:
        """adapt() does not raise when given a callable that cannot be inspected."""

        class Uninspectable:
            def __call__(self, hand: Hand) -> str:
                return "stand"

            # Force inspect.signature() to raise ValueError
            @property  # type: ignore[override]
            def __wrapped__(self):  # noqa: ANN202
                raise ValueError("not inspectable")

        obj = Uninspectable()
        # Whether or not inspect succeeds, adapt() must not raise
        adapted = adapt(obj)
        hand = _make_hand("9", "6")
        upcard = _make_card("3")
        result = adapted(hand, upcard)
        assert result in ("hit", "stand")


class TestHumanStrategy:
    def test_human_strategy_hit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """human_strategy returns 'hit' when input is 'h'."""
        monkeypatch.setattr("builtins.input", lambda _: "h")
        hand = _make_hand("7", "6")
        upcard = _make_card("9")
        assert human_strategy(hand, upcard) == "hit"

    def test_human_strategy_stand(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """human_strategy returns 'stand' when input is 's'."""
        monkeypatch.setattr("builtins.input", lambda _: "s")
        hand = _make_hand("King", "8")
        upcard = _make_card("5")
        assert human_strategy(hand, upcard) == "stand"

    def test_human_strategy_retries_on_invalid(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """human_strategy loops on invalid input and eventually returns the valid response."""
        responses = iter(["x", "?", "h"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        hand = _make_hand("5", "3")
        upcard = _make_card("7")
        assert human_strategy(hand, upcard) == "hit"

    def test_human_strategy_accepts_full_word_hit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """human_strategy accepts 'hit' as full word."""
        monkeypatch.setattr("builtins.input", lambda _: "hit")
        hand = _make_hand("4", "6")
        upcard = _make_card("2")
        assert human_strategy(hand, upcard) == "hit"

    def test_human_strategy_accepts_full_word_stand(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """human_strategy accepts 'stand' as full word."""
        monkeypatch.setattr("builtins.input", lambda _: "stand")
        hand = _make_hand("King", "Queen")
        upcard = _make_card("6")
        assert human_strategy(hand, upcard) == "stand"


class TestSessionStrategyIntegration:
    def test_session_passes_upcard_to_strategy(self, tmp_path: Path, monkeypatch) -> None:
        """play_table_session passes the dealer upcard (a Card) as second arg to strategy."""
        received_upcards: list = []

        def recording_strategy(hand: Hand, upcard: Card) -> str:
            received_upcards.append(upcard)
            return "stand"

        monkeypatch.chdir(tmp_path)
        table = Table(
            tableId="t-ice6",
            maxSeats=7,
            minBet=1.0,
            maxBet=100.0,
            numDecks=1,
            players=[Player(name="Alice", strategy=recording_strategy, wallet=100.0)],
            dealer=Dealer(),
            houseRules=HouseRules(blackjackPayout=1.5, dealerHitsOnSoft17=False),
        )
        play_table_session(table, seed=1, max_hands=1)
        # Strategy must have been called with a Card as second argument
        assert len(received_upcards) >= 1
        assert all(isinstance(u, Card) for u in received_upcards)

    def test_existing_one_arg_strategies_still_work(self, tmp_path: Path, monkeypatch) -> None:
        """One-arg strategies continue to work unchanged after the interface extension."""

        def stand_strategy(hand: Hand) -> str:
            return "stand"

        monkeypatch.chdir(tmp_path)
        table = Table(
            tableId="t-compat",
            maxSeats=7,
            minBet=1.0,
            maxBet=100.0,
            numDecks=1,
            players=[Player(name="Bob", strategy=stand_strategy, wallet=100.0)],
            dealer=Dealer(),
            houseRules=HouseRules(blackjackPayout=1.5, dealerHitsOnSoft17=False),
        )
        # Must complete without error
        play_table_session(table, seed=42, max_hands=1)
